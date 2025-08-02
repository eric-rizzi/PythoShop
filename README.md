# PythoShop

This project enables students who are learning Python to create their own
photo editing software. It is intended to be a "capstone project" for high
school students at the end of an "Introduction to Python" course. While
completing the project, students learn about bitmaps, operating on files,
functions, and loops.

The code is intended to be a basic framework that allows for quick creation
of (and feedback on) various filters/tools that students create. For example,
one of the first filters that students are asked to create is a `change_pixel`
function. Upon implementing the function, students will be able to use it
to alter a photo in the PythoShop GUI. Further, teachers will be able to test
the correctness of their efforts by running it through a series of automated
tests.

> Note: due to the end of year scramble, a lot of the teacher-side automation
  is not working. It's a good system (relying on GoogleDocs to ease auto-
  grading), but I kind of messed it up and it needs to be recreated.

## Setup

In order to properly configure their class, teachers need to complete the
following steps:
1. Contact the owner of this repository for the canonical solutions in
   `ImageManip.py`.
2. Copy `ImageManip.py` into the top level of this directory.
3. Run `tests/pickleImages.py` to create the "expected outputs" to provide
   students quick feedback via the built-in testing system.
4. Distribute the basic skeleton project to students by:
    - Filling in the paths the student's GoogleDrive folder into `admin/students.py`
    - Distributing all necessary files via `admin/updateStudentsFiles.py`

## Class Flow

The overall vision of a student/class completing this project is to slowly
increase the complexity that they are exposed to. This is done by having
students use a GoogleDrive folder (shared with the instructor) where the
initial, base files are supplemented by additional problems/test files over
time.

### First week

Distribute to students a zipped workspace (on Schoology) that contains:

- vscode workspace files
    - `pythoshop.code-workspace`
    - `.vscode` folder
- PythoShop application files
    - `pythoShop.py`
    - `pythoShop.kv`
    - `pythoShopExports.py`
- Base file that students will be working on
    - `ImageManip.py`
- Image files
    - `bear.bmp` ... `wider.bmp`
    - Expected output files
    - Pickled images
- Test files
    - `config.py`
    - `testBase*.py`
    - `testRunner.py` (with grade portion cancelled out)
    - `testTool.py`
    - `test_01_change_pixel.py`
    - `test_10_*.py` (first week of regular problems and extensions)

From there, students will have enough material to work on (when paired with the
Schoology assignments) for the whole week.

### Later weeks

As weeks progress, navigate to the `admin/updateStudentFiles.py` file and
alter what is copied into the students' GoogleDrive folder.

### Further Alterations

At some point, you will want to introduce the "grades" to the students. Doing
this too soon makes some of them become a bit... nervous. Therefore, it's
worth commenting out the "Grades Summary" portion of `tests/testRunner.py
for a while.

## Teaching PythoShop:

The lesson plans for PythoShop can be found
[here](https://github.com/eric-rizzi/ucls-hs-intro-to-cs/tree/mainline/CourseMaterial/04_pythoshop).
The accompanying slides for the lessons can be found
[here](https://docs.google.com/presentation/d/1Xv8M9BBIJSzkkeBRApU6jNcrwXNBSvQWgDNRtn-uKw8/edit?usp=sharing).

- [Introducing PythoShop](https://docs.google.com/presentation/d/1Xv8M9BBIJSzkkeBRApU6jNcrwXNBSvQWgDNRtn-uKw8)
- [Change a Pixel](https://docs.google.com/document/d/1LGuQQPHvYpMwVn269lRUtp7xrQAV-5hhj4m443Yi9n0)
- [Change Multiple Pixels](https://docs.google.com/document/d/1xbOrwUMz_48eGLWHmHnraCnf2AQEE11Qt9aEErpWM5c)
- [Drawing Lines](https://docs.google.com/document/d/1wijKCu1sCK8tCembiKr5q3JuGVCXh5LgpYa_k9Daz2c)
- [Changing Parts of Pixels](https://docs.google.com/document/d/1uXbiT-LXxW9RWpdDqQPeNiizP-wa0hThpcdDe1A90_I)
- [Changing Pixels Based on Values](https://docs.google.com/document/d/1b-_Eq48VScdFNqXwF3JEXckwO5AoHbu4r5UPynUX7JQ)
- [Conditional Modification of Pixels](https://docs.google.com/document/d/1E3v36HUh18ogVqMij1zDeYAKccBm6d_4fSuFeeACrlc)
- [Blending Pictures](https://docs.google.com/document/d/16Ojx0zLR8qMaISlor8awAbqrqwX1n94_QZEQiyfUnLw)
- [Pixel Positions](https://docs.google.com/document/d/1E35rBAmndMOJv5E_0s2g_jLdgOgs1UGzaxkVFDe1eDA)


