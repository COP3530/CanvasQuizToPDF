# canvasgrading
This repo contains modified source code from canvas grading repo which can be found here: https://github.com/ubc-cpsc/canvasgrading/tree/d55f4b0868469de5527266278f3098ffcfb6edbd

### Newly adapted version for printing Canvas Quizzes
Run the command `python3 quiz2pdf.py -t [API_KEY_TOKEN] -c [COURSE_ID] -q [QUIZ_ID] --template-only` to produce the html and the corresponding pdf. 

The script will filter out the questions that are in a question group with pick_count = 0. 

The css styling for the questions are styled similar to that of canvas. 
* Multiple answer question: empty square
* Multiple choice question: empty circle

### Old Version 
This repo contains several scripts that use the Canvas API to manage
quizzes and assignments on Canvas.

All scripts will receive an argument that is based on an access token
associated to your account (https://canvas.ubc.ca/profile/settings,
see Approved Integrations). This token can be provided directly as a
string in the command-line using the `-t TOKEN` option, or saved into
a text file and provided with the `-f TOKENFILE` option.

All scripts will also include an optional argument: `-c COURSE`,
corresponding to the ID of the course on Canvas. If you don't specify
it, the script lists all courses you have access to and asks for a
course. The ID can be obtained by looking at the URL on Canvas, it's
the number after 'courses/'.

All scripts that involve quizzes will also include the `-q QUIZ`
argument, corresponding to the ID of the quiz.  If you don't specify
it, the script lists all quizzes from the course you selected and asks
for a quiz. The ID can be obtained by looking at the URL on Canvas
when you open the quiz, it's the number after 'quizzes/'.

For assignment-based quizzes, the `-a ASSIGNMENT` argument is also
provided and works in the same way as the quiz argument above.

Please submit any questions or comments to jonatan@cs.ubc.ca.

## quiz2pdf.py

This is a script that converts a Canvas quiz to a PDF suitable for
Gradescope. In addition to the `-t/-f`, `-c` and `-q` arguments listed
above, it also receives the following arguments, all optional:

1. `-l CLASSLIST`: The name of a classlist CSV file containing at
least the columns SNUM and ACCT. You can generate it on the department
computers with a command like: `classlist <course_num> -T -f
"%SN,%ACCT"`. If provided, the PDF will use the student account as
identifier in the first page. If not provided, the PDF will use the
student's name and student number for identification. Note that, due
to FIPPA, the name/student number option is only suitable for use in
gradescope.ca, though its use gives significantly better recognition
by Canvas automatic matching algorithm.

2. `-p PREFIX`: A string used as prefix for the output
files. Can also be used to specify a different directory to store the
data in (e.g., `~/cs299/Final/FinalExam`). If not specified, a prefix
is generated based on the quiz name, removing any non-alphanumeric
characters (spaces, etc.).

3. `--only-question QID QID ...`: A list of question IDs to
include. If not specified, all questions are included. The ID of the
question can be obtained by running this script with all questions
(without this argument), the number provided before the text of each
question is the question ID. Alternatively, you may obtain the
question ID by using the JSON sync script below.

4. `--not-question QID QID ...`: A list of question IDs to exclude. If
not specified, all questions are included. The ID of the question can
be obtained by running this script with all questions (without this
argument), the number provided before the text of each question is the
question ID. Alternatively, you may obtain the question ID by using
the JSON sync script below.

5. `-d`: Enter debug mode. In this mode, only the first 10 submissions
are loaded from Canvas, and an extra `debug.json` file is
generated. This can be used to test the configuration, style or the
script itself.

6. `--css`: An additional CSS file to be used for this quiz. The
existing `canvasquiz.css` file in this repo is always added, this CSS
file can be used for question-specific or exam-specific formatting.

7. `--template-only`: If provided, only the template is created, with
no student submission.

The script requires the use of the `weasyprint` Python library. As
system package installation may be required, see
https://weasyprint.readthedocs.io/en/stable/install.html
before installing with something like:

    pip3 install --user weasyprint

The script will connect to the Canvas API to get the latest responses
from Canvas itself. The program will generate a file
`XXX_template.html` and `XXX_template.html.pdf`, where `XXX` is the
string from the first argument; the PDF file can be used as a template
for a quiz on Gradescope. The script will also create a series of
files named `XXX_exams_YY.html` and `XXX_exams_YY.html.pdf`, where YY
is a counter; each file contains up to 20 exams, which can be uploaded
to Gradescope as exams.

The script also creates a file named `XXX_raw_answers.zip` containing
a file for each essay question in the quiz. For quizzes with multiple
attempts allowed, these files will be created for all attempts. This
file is named `answer_<QID>_<STUD>_v<ATT>.html`, where `<QID>`,
`<STUD>` and `<ATT>` are the question ID, student number (or account)
and attempt number, respectively. These can be useful in cases where
either the answer is too long to fit in a PDF page, or if the marker
wants to copy that answer to test it (e.g., in an IDE). Also, for all
file upload type questions, the uploads will be saved in the same
file, in a file named `answer_<QID>_<STUD>_v<ATT>_<FN>`, where FN is
the file name originally used by the submitter.

The script supports all question types allowed in Canvas classic
quizzes, including text-only, essay, file upload, fill-in the blank
(or multiple blanks), multiple choice (including true/false and
multiple answers), multiple dropdowns, matching, numerical answers and
formula (calculated) questions. It also supports question groups, in
which case each question version is saved in a different page, and any
question submission that doesn't include a specific question will list
the answer as "NO SUBMISSION", with an explanation text. For file
upload questions, the answer will list the file names included in the
answer, which can be found in the raw answers file listed above. For
all other questions, the answer will be listed in the PDF itself. If
the question plus answer don't fit a single page, it will be
truncated, and you may find the answer in the raw answers file above.

Given some limitations of the Canvas API, this script does not support
question groups linked to question banks. If using question groups,
the questions must be included in the quiz itself instead of in the
bank only.

## License
This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).
