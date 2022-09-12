#! /usr/bin/python3

import os
import csv
from pprint import pprint
import re
from os import path
import json
import zipfile
import argparse
import requests
import weasyprint

import canvas


def start_file(file_name):
    if path.exists(file_name):
        os.rename(file_name, file_name + '~')
    htmlfile = open(file_name, 'w')
    htmlfile.write('''<!DOCTYPE html>
    <html>
      <head></head>
      <body>
    ''')
    htmlfile_list.append(file_name)
    return htmlfile


def check_question_group_pick_count_zero(quiz_id, question_id, api_key_token):
    API_URL = "https://ufl.instructure.com/api/v1/courses/460732/quizzes/" + \
        str(quiz_id) + "/groups/" + str(question_id)

    token_header = {'Authorization': f'Bearer {api_key_token}'}
    response = requests.get(API_URL, headers=token_header)
    obj = response.json()

    if obj['pick_count'] == 0:
        return True

    return False


def write_exam_file(quiz_id, api_key_token, htmlfile, question_dict, quiz_submission=None):
    acct = ''
    snum = ''
    sname = ''
    answers = {}
    sub_questions = {}
    num_attempts = 0

    if args.classlist:
        htmlfile.write(f'''<div class='student-wrapper'>
        <span class='account-label'>Account:</span>
        <span><span class='account'>{acct}</span></span>
        </div>''')
    else:
        htmlfile.write(f'''<div class='student-wrapper'>
        <span class='snum-label'>Student Number:</span>
        <span><span class='snum'>{snum}</span></span>
        <span class='sname-label'>Name:</span>
        <span><span class='sname'>{sname}</span></span>
        </div>''')

    qnum = 1
    for (question_id, question) in question_dict.items():
        # Discard the question if it's not picked on canvas
        if question['quiz_group_id']:
            if check_question_group_pick_count_zero(
                    quiz_id, question['quiz_group_id'], api_key_token):
                continue

        question_name = question['question_name']
        question_text = question['question_text']

        question_type = question['question_type']
        if question_id in sub_questions and question_type == 'calculated_question':
            question_text = sub_questions[question_id]['question_text']
        if question_type == 'text_only_question':
            htmlfile.write(
                f"<div class='text-only-question'>{question_text}</div>")
            continue

        worth = question['points_possible']
        answer = None
        answer_text = ''
        points = ''

        if question_id in answers:
            answer = answers[question_id]
            answer_text = answer['text'] if 'text' in answer else ''
            points = answer['points']
        elif quiz_submission is not None:
            question_type = None  # To avoid formatting of multiple-choice
            answer_text = '''
            *** NO SUBMISSION ***<br/><br/>
            This typically means that this question is part of a question
            group, and the student did not receive this question in the
            group (i.e., the student answered a different question in
            this set).
            '''

        if question_type in ('calculated_question',
                             'short_answer_question',
                             'essay_question',
                             'numerical_question'):
            answer_text = '''
            <div>
                <input type="text" class="question_input">
            </div>
            '''
            pass  # use answer exactly as provided
        elif question_type in ('true_false_question',
                               'multiple_choice_question',
                               'multiple_answers_question'):
            answer_text = ''
            for pan in question['answers']:
                if question_type == 'multiple_answers_question':
                    key = f"answer_{pan['id']}"
                    choice = answer[key] if answer is not None and key in answer else ''
                    if choice == '0':
                        choice = ''
                else:
                    choice = 'X' if answer is not None and 'answer_id' in answer and pan[
                        'id'] == answer['answer_id'] else ''

                # Use a square for multiple answer question and use a circle for others
                choiceIconType = "&#9723" if question_type == 'multiple_answers_question' else "&#9711"
                answer_text += f'''
                    <div class="mc-item">
                        <label class="mc-row">
                            <div class="answer_label">{choiceIconType} {pan["text"]}</div>
                        </label>
                    </div>
                '''

        elif question_type in ('fill_in_multiple_blanks_question',
                               'multiple_dropdowns_question'):
            answer_text = '<table class="multiple-blanks-table">'
            tokens = []
            dd_answers = {}
            for pan in question['answers']:
                if pan['blank_id'] not in tokens:
                    tokens.append(pan['blank_id'])
                dd_answers[pan['id']] = pan['text']
            for token in tokens:
                key = f'answer_for_{token}'
                choice = answer[key] if answer is not None and key in answer else ''
                if choice != '' and question_type == 'multiple_dropdowns_question' and choice in dd_answers:
                    choice = dd_answers[choice]
                answer_text += '<tr>'
                answer_text += f'<td class="multiple-blanks-token">{token}</td>'
                answer_text += '<td>=></td>'
                answer_text += f'<td class=multiple-blanks-answer>{choice}</td>'
                answer_text += '</tr>'
            answer_text += '</table>'

        elif question_type == 'matching_question':
            answer_text = '<table class="multiple-blanks-table">'
            matches = {}
            for match in question['matches']:
                matches[f"{match['match_id']}"] = match['text']
            for pan in question['answers']:
                key = f"answer_{pan['id']}"
                choice = matches[answer[key]
                                 ] if answer is not None and key in answer and answer[key] in matches else ''
                answer_text += '<tr>'
                answer_text += f'<td class="multiple-blanks-token">{pan["text"]}</td>'
                answer_text += '<td>=></td>'
                answer_text += f'<td class="multiple-blanks-answer">{choice}</td>'
                answer_text += '</tr>'
            answer_text += '</table>'

        elif question_type == 'file_upload_question':
            pass  # This is handled in the processing of history above.
        elif question_type is not None:
            raise ValueError(f'Invalid question type: "{question_type}"')

        num_attempts_text = '' if num_attempts <= 1 else f' ({num_attempts} attempts)'
        # <div class="question-preamble question-{question_id}"></div>
        htmlfile.write(f'''
        <div class=full-question-container>
            <div class="question-title-container">
                <span class="question-title">Question {qnum}</span>

                <span class="question-points-holder">
                    <span class="question-points">{worth}</span> pts
                </span>
            </div>

            <div class="question-answer-container">
                <div class=question>{question_text}</div>
                <div class=answer>{answer_text}</div>
            </div>
            </div>
        </div>
        <br>
        <br>
        ''')
        qnum += 1


def end_file(htmlfile):
    htmlfile.write('</body>\n</html>')
    htmlfile.close()


def question_included(qid):
    if args.not_question and qid in args.not_question:
        return False
    if args.only_question:
        return qid in args.only_question
    return True


parser = argparse.ArgumentParser()
canvas.Canvas.add_arguments(parser, quiz=True)
parser.add_argument("-l", "--classlist", type=str,  # type=argparse.FileType('r', newline=''),
                    help="""CSV file containing student number and account.
                    If used, account is provided on the front page, otherwise
                    it will include name and student number.""")
parser.add_argument("-p", "--output-prefix",
                    help="Path/prefix for output files")
group = parser.add_mutually_exclusive_group()
group.add_argument("--only-question", action='extend', nargs='+', type=int, metavar="QUESTIONID",
                   help="Questions to include")
group.add_argument("--not-question", action='extend', nargs='+', type=int, metavar="QUESTIONID",
                   help="Questions to exclude")
parser.add_argument("--css",
                    help="Additional CSS file to use in PDF creation.")
parser.add_argument("--template-only", action='store_true',
                    help="Create only the template, without students.")
args = parser.parse_args()

canvas = canvas.Canvas(args=args)

student_accounts = {}
htmlfile_list = []

if args.classlist:
    print('Reading classlist...')

    with open(args.classlist, 'r', newline='') as file:
        reader = csv.DictReader(file)
        if 'SNUM' not in reader.fieldnames:
            raise ValueError(
                'Classlist CSV file does not contain student number.')
        if 'ACCT' not in reader.fieldnames:
            raise ValueError('Classlist CSV file does not contain account.')
        for row in reader:
            student_accounts[row['SNUM']] = row['ACCT']

print('Reading data from Canvas...')
course = canvas.course(args.course, prompt_if_needed=True)
print(f"Using course: {course['term']['name']} / {course['course_code']}")

quiz = course.quiz(args.quiz, prompt_if_needed=True)
print(f"Using quiz: {quiz['title']}")

if not args.output_prefix:
    args.output_prefix = re.sub(r'[^A-Za-z0-9-_]+', '', quiz['title'])
    print(f'Using prefix: {args.output_prefix}')

# Reading questions
print('Retrieving quiz questions...')
(questions, groups) = quiz.questions(question_included)

print('Retrieving quiz submissions...')
if args.template_only:
    quiz_submissions = []
    submissions = {}
else:
    (quiz_submissions, submissions) = quiz.submissions()

print('Generating HTML files...')

file_no = 1
template_file = start_file(f'{args.output_prefix}_template.html')
if not args.template_only:
    exams_file = start_file(f'{args.output_prefix}_exams_{file_no}.html')
    rawanswers_file = zipfile.ZipFile(
        f'{args.output_prefix}_raw_answers.zip', 'w')

write_exam_file(args.quiz, args.canvas_token, template_file, questions)

if args.debug:
    with open('debug.json', 'w') as file:
        data = {}
        data['quiz'] = quiz.data
        data['questions'] = questions
        data['quiz_submissions'] = quiz_submissions
        data['submissions'] = submissions
        json.dump(data, file, indent=2)

end_file(template_file)
if not args.template_only:
    end_file(exams_file)
    rawanswers_file.close()

print('\nConverting to PDF...')
css = [weasyprint.CSS(path.join(path.dirname(__file__), 'canvasquiz.css'))]
if args.css:
    css.append(weasyprint.CSS(args.css))

for file in htmlfile_list:
    print(f'{file}...  ', end='\r')
    weasyprint.HTML(filename=file).write_pdf(
        f'{file}.pdf', stylesheets=css)

print('\nDONE. Created files:')
for file in htmlfile_list:
    print(f'- {file}.pdf')
if not args.template_only:
    print(f'- {args.output_prefix}_raw_answers.zip')
