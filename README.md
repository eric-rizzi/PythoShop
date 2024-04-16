# PythoShop

## To build "expected outputs" for tests

`admin/pickle_images.py`

## To copy required files into student's GoogleDocs

`admin/update_students_files.py`

## Class flow

The overall goal is to slowly increase the complexity of the project. This is
done by having students use a GoogleDrive folder (shared with the instructor)
where the initial, base files are supplemented by additional files being added
over time.

### First week

Distribute to students a zipped workspace (on Schoology) that contains:
- vscode workspace files
    - `pythoshop.code-workspace`
    - `.vscode` folder
- PythoShop application files
    - `pythoshop.py`
    - `pythoshop.kv`
    - `pythoshop_exports.py`
- Base file that students will be working on
    - `image_manip.py`
- Image files
    - `bear.bmp` ... `wider.bmp`
    - Expected output files
    - Pickled images
- Test files
    - `config.py`
    - `test_base*.py`
    - `test_runner.py` (with grade portion cancelled out)
    - `test_tool.py`
    - `test_01_change_pixel.py`
    - `test_10_*.py` (first week of regular problems and extensions)

From there, students will have enough material to work on (when paired with the
Schoology assignments) for the whole week.

### Later weeks

As weeks progress, navigate to the `admin/update_student_files.py` file and
alter the `ASSIGNMENT_NUMBER` variable. This variable represents which week
the students are in. For example, setting it to `3` will copy all the files
required for the first three assignments into the student's GoogleDrive folder.
