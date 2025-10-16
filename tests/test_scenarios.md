# Test Scenarios for Restaurant Access Control System

## Overview
This document outlines comprehensive test scenarios to validate the functionality of the Restaurant Access Control System.

## Test Environment Setup

### Prerequisites
- Python 3.8+ installed
- All dependencies from requirements.txt installed
- Application successfully launched
- Admin authentication completed

### Test Data
- **Test Images**: Prepare 5-10 clear photos of different people (one face per image)
- **Student IDs**: Use realistic student ID format (e.g., 20240001, 20240002)
- **Names**: Use realistic French names
- **Balances**: Various amounts (€0, €2, €5, €25, €50)

## Test Scenarios

### Scenario 1: System Startup and Authentication

**Objective**: Verify system starts correctly and admin authentication works

**Steps**:
1. Run `python main.py`
2. Verify dependency check passes
3. Enter admin credentials in login dialog
4. Verify main application opens

**Test Cases**:
- **TC1.1**: Valid admin credentials (`admin` / `restaurant123`)
- **TC1.2**: Invalid credentials (`wrong` / `password`)
- **TC1.3**: Empty credentials
- **TC1.4**: Cancel authentication dialog

**Expected Results**:
- TC1.1: Authentication successful, main GUI opens
- TC1.2: Error message, authentication fails
- TC1.3: Warning message about empty fields
- TC1.4: Application exits gracefully

### Scenario 2: Student Registration

**Objective**: Test adding new students to the system

**Test Data**:
```
Student 1: ID=20240001, Name=Jean Dupont, Balance=€50.00
Student 2: ID=20240002, Name=Marie Martin, Balance=€25.00
Student 3: ID=20240003, Name=Pierre Durand, Balance=€0.00
```

**Steps**:
1. Switch to "Student Management" mode
2. Go to "Add Student" tab
3. Fill in student information
4. Select valid photo file
5. Click "Add Student"

**Test Cases**:
- **TC2.1**: Add student with all valid information
- **TC2.2**: Add student with duplicate ID
- **TC2.3**: Add student with missing fields
- **TC2.4**: Add student with invalid image (no face)
- **TC2.5**: Add student with invalid image (multiple faces)
- **TC2.6**: Add student with invalid balance format

**Expected Results**:
- TC2.1: Student added successfully, appears in database
- TC2.2: Error message "Student ID already exists"
- TC2.3: Warning about missing fields
- TC2.4: Warning about no faces detected
- TC2.5: Warning about multiple faces
- TC2.6: Warning about invalid balance format

### Scenario 3: Face Recognition Database

**Objective**: Verify face encoding and database operations

**Steps**:
1. Add 3-5 students with photos
2. Go to "View Students" tab
3. Click "Reload Face Database"
4. Verify face encodings are loaded

**Test Cases**:
- **TC3.1**: Load face database with valid images
- **TC3.2**: Load database with some invalid images
- **TC3.3**: Load empty database (no images)

**Expected Results**:
- TC3.1: Success message with correct count
- TC3.2: Warning messages for invalid images, success for valid ones
- TC3.3: Message indicating no faces loaded

### Scenario 4: Camera Access Control

**Objective**: Test live camera recognition and access control

**Prerequisites**: Camera connected and working

**Steps**:
1. Switch to "Access Control" mode
2. Click "Start Camera"
3. Position registered student in front of camera
4. Click "Capture & Identify"

**Test Cases**:
- **TC4.1**: Registered student with sufficient balance (≥€4)
- **TC4.2**: Registered student with insufficient balance (<€4)
- **TC4.3**: Unregistered person
- **TC4.4**: No person in camera view
- **TC4.5**: Multiple people in camera view

**Expected Results**:
- TC4.1: "ACCESS GRANTED", balance deducted by €4
- TC4.2: "ACCESS DENIED", insufficient balance message
- TC4.3: "No face recognized" message
- TC4.4: "No face detected" message
- TC4.5: First face recognized (if any are registered)

### Scenario 5: File Upload Recognition

**Objective**: Test image file upload recognition

**Steps**:
1. Switch to "Access Control" mode
2. Click "Select Image File"
3. Choose test image file

**Test Cases**:
- **TC5.1**: Image of registered student with sufficient balance
- **TC5.2**: Image of registered student with insufficient balance
- **TC5.3**: Image of unregistered person
- **TC5.4**: Invalid image file (corrupted)
- **TC5.5**: Image with no faces
- **TC5.6**: Image with multiple faces

**Expected Results**:
- TC5.1: "ACCESS GRANTED", balance deducted
- TC5.2: "ACCESS DENIED", balance insufficient
- TC5.3: "No face recognized"
- TC5.4: Error message about invalid file
- TC5.5: "No face detected" message
- TC5.6: First face processed if recognized

### Scenario 6: Balance Management

**Objective**: Test balance operations

**Test Data**:
- Student ID: 20240001 (existing student)
- Add amount: €20.00

**Steps**:
1. Go to "Student Management" → "Manage Balance"
2. Enter student ID
3. Perform balance operations

**Test Cases**:
- **TC6.1**: Check balance for existing student
- **TC6.2**: Check balance for non-existent student
- **TC6.3**: Add balance with valid amount
- **TC6.4**: Add balance with invalid amount (text)
- **TC6.5**: Add negative balance

**Expected Results**:
- TC6.1: Current balance displayed
- TC6.2: "Student not found" message
- TC6.3: Balance updated, success message
- TC6.4: Error about invalid number format
- TC6.5: Balance decreases (or error if designed to prevent)

### Scenario 7: Student List Management

**Objective**: Test student viewing and data management

**Steps**:
1. Add several students
2. Go to "View Students" tab
3. Perform list operations

**Test Cases**:
- **TC7.1**: View all students in list
- **TC7.2**: Refresh student list after changes
- **TC7.3**: Check student information accuracy
- **TC7.4**: View access statistics

**Expected Results**:
- TC7.1: All students displayed with correct information
- TC7.2: List updates with new/changed data
- TC7.3: All displayed data matches database
- TC7.4: Access counts and dates shown correctly

### Scenario 8: Error Handling and Edge Cases

**Objective**: Test system robustness

**Test Cases**:
- **TC8.1**: Delete database file while app running
- **TC8.2**: Delete image file after student registration
- **TC8.3**: Disconnect camera during operation
- **TC8.4**: Very large image file (>10MB)
- **TC8.5**: Very small image file (<1KB)
- **TC8.6**: Maximum students in database (100+)

**Expected Results**:
- TC8.1: Graceful handling, create new database
- TC8.2: Error message about missing image
- TC8.3: Appropriate error message
- TC8.4: Handling or warning about file size
- TC8.5: Error about invalid image
- TC8.6: Performance remains acceptable

### Scenario 9: Data Persistence

**Objective**: Verify data is saved and loaded correctly

**Steps**:
1. Add students and perform access operations
2. Close application
3. Restart application
4. Verify data persistence

**Test Cases**:
- **TC9.1**: Student data persists after restart
- **TC9.2**: Balance changes persist after restart
- **TC9.3**: Access statistics persist after restart
- **TC9.4**: Face encodings reload correctly

**Expected Results**:
- TC9.1: All students still in database
- TC9.2: Updated balances maintained
- TC9.3: Access counts and dates preserved
- TC9.4: Face recognition still works for all students

### Scenario 10: Performance Testing

**Objective**: Test system performance under normal conditions

**Test Cases**:
- **TC10.1**: Recognition speed with 1 student
- **TC10.2**: Recognition speed with 50 students
- **TC10.3**: Database operations with 100 students
- **TC10.4**: Camera feed frame rate
- **TC10.5**: Memory usage during operations

**Expected Results**:
- TC10.1: Recognition within 2 seconds
- TC10.2: Recognition within 5 seconds
- TC10.3: Database operations < 1 second
- TC10.4: Smooth camera feed (20+ FPS)
- TC10.5: Memory usage < 200MB

## Test Execution Guidelines

### Before Testing
1. Backup any existing data
2. Prepare test images and data
3. Ensure good lighting for camera tests
4. Document test environment details

### During Testing
1. Record actual results for each test case
2. Take screenshots of important states
3. Note any unexpected behavior
4. Time performance-critical operations

### After Testing
1. Document all issues found
2. Classify issues by severity
3. Provide steps to reproduce problems
4. Suggest improvements or fixes

## Test Results Template

```
Test Case: TC[X.Y]
Date: [Date]
Tester: [Name]
Environment: [OS, Python version, etc.]

Steps Executed:
1. [Step 1]
2. [Step 2]
...

Expected Result: [Expected outcome]
Actual Result: [What actually happened]
Status: [PASS/FAIL]
Notes: [Additional observations]
Screenshot: [If applicable]
```

## Success Criteria

The system passes testing if:
- All critical functionality works as expected (TC1-6)
- Error handling is appropriate (TC8)
- Data persistence works correctly (TC9)
- Performance meets acceptable standards (TC10)
- No critical bugs are found
- User interface is intuitive and responsive

## Known Limitations

Document any known limitations during testing:
- Camera compatibility issues
- Lighting requirements for recognition
- Image format restrictions
- Performance with large datasets
- Operating system specific behaviors