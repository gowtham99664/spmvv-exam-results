# Excel Upload Template Guide

## Overview
This document provides a guide for preparing Excel files to upload student results to the SPMVV Exam Results Management System.

## File Requirements
- **Format**: Excel (.xlsx or .xls)
- **Max Size**: 10 MB
- **Structure**: Headers in Row 1, Data from Row 2 onwards

## Required Columns

### Basic Information
1. **Roll Number** (Required)
   - Student's unique roll number
   - Example: 2023CS001

2. **Student Name** (Required)
   - Full name of the student
   - Example: Rajesh Kumar

3. **Semester** (Required)
   - Numeric value (1, 2, 3, etc.)
   - Example: 3

4. **Result Type** (Required)
   - Must be one of: Regular, Supplementary, Both (displayed as "Regular and Supplementary")
   - Example: Regular

### Subject Information (Repeat for each subject)

For each subject (1 through N), include these columns:

5. **Subject N Code** (Required)
   - Subject code
   - Example: CS301

6. **Subject N Name** (Required)
   - Full subject name
   - Example: Database Management Systems

7. **Subject N Internal** (Optional)
   - Internal marks
   - Example: 18

8. **Subject N External** (Optional)
   - External marks
   - Example: 65

9. **Subject N Total** (Optional)
   - Total marks
   - Example: 83

10. **Subject N Result** (Required)
    - Must be one of: Pass, Fail, Absent
    - Example: Pass

11. **Subject N Grade** (Optional)
    - Grade obtained
    - Example: A

### Overall Results (Optional)

12. **Overall Result** (Optional)
    - Overall result status
    - Example: Pass

13. **Overall Grade** (Optional)
    - Overall grade
    - Example: A

## Sample Excel Structure

```
| Roll Number | Student Name   | Semester | Result Type | Subject 1 Code | Subject 1 Name | Subject 1 Internal | Subject 1 External | Subject 1 Total | Subject 1 Result | Subject 1 Grade | Subject 2 Code | ... | Overall Result | Overall Grade |
|-------------|----------------|----------|-------------|----------------|----------------|--------------------|--------------------|-----------------|-----------------|-----------------|-----------------|----|----------------|---------------|
| 2023CS001   | Rajesh Kumar   | 3        | Regular     | CS301          | DBMS           | 18                 | 65                 | 83              | Pass            | A               | CS302           | ... | Pass           | A             |
| 2023CS002   | Priya Sharma   | 3        | Regular     | CS301          | DBMS           | 15                 | 58                 | 73              | Pass            | B               | CS302           | ... | Pass           | B             |
```

## Validation Rules

### Data Validation
1. **Roll Number**: Must be unique per semester and result type
2. **Semester**: Must be a positive integer
3. **Result Type**: Case-insensitive (regular, REGULAR, Regular all work)
4. **Subject Result**: Must be Pass, Fail, or Absent
5. **Marks**: If provided, must be numeric
6. **Minimum**: At least one subject must be present

### File Validation
- File must have headers in the first row
- At least one data row required
- Empty rows are skipped
- Duplicate entries (same roll number, semester, result type) will update existing records

## Common Errors and Solutions

### Error: "Missing required column: Roll Number"
**Solution**: Ensure the first row contains exactly "Roll Number" as a header

### Error: "Invalid Result Type"
**Solution**: Result Type must be exactly one of: Regular, Supplementary, Both

### Error: "Invalid Semester value"
**Solution**: Semester must be a positive number (1, 2, 3, etc.)

### Error: "No subjects found"
**Solution**: Ensure you have at least:
- Subject 1 Code
- Subject 1 Name
- Subject 1 Result

### Error: "File size exceeds maximum"
**Solution**: Reduce file size to under 10 MB. Consider splitting into multiple uploads.

## Best Practices

1. **Use Template**: Create a template Excel file with proper headers
2. **Test First**: Upload a small batch (5-10 students) to verify format
3. **Check Data**: Verify all data before upload - no partial imports are done
4. **Backup**: Keep backup of original Excel files
5. **Consistent Naming**: Use consistent naming for Result Type (always "Regular", not "REGULAR")
6. **No Special Characters**: Avoid special characters in names that might cause encoding issues

## Example: 3 Subjects Per Student

```
| Roll Number | Student Name | Semester | Result Type | Subject 1 Code | Subject 1 Name | Subject 1 Internal | Subject 1 External | Subject 1 Total | Subject 1 Result | Subject 1 Grade | Subject 2 Code | Subject 2 Name | Subject 2 Internal | Subject 2 External | Subject 2 Total | Subject 2 Result | Subject 2 Grade | Subject 3 Code | Subject 3 Name | Subject 3 Internal | Subject 3 External | Subject 3 Total | Subject 3 Result | Subject 3 Grade | Overall Result | Overall Grade |
|-------------|--------------|----------|-------------|----------------|----------------|--------------------|--------------------|-----------------|-----------------|-----------------|-----------------|-----------------|--------------------|--------------------|-----------------|-----------------|-----------------|-----------------|-----------------|--------------------|--------------------|-----------------|-----------------|-----------------|--------------------|---------------|
| 2023CS001   | Rajesh Kumar | 3        | Regular     | CS301          | DBMS           | 18                 | 65                 | 83              | Pass            | A               | CS302           | OS              | 17                 | 62                 | 79              | Pass            | A               | CS303           | Networks        | 16                 | 60                 | 76              | Pass            | B               | Pass           | A             |
```

## After Upload

After successful upload:
- Students automatically receive notifications
- Results are immediately available to students in their dashboard
- Admin can view uploaded results in the results section
- All actions are logged in audit logs

## Troubleshooting

If you encounter errors:
1. Check error messages carefully - they indicate the exact row and issue
2. Verify all required columns are present with exact names
3. Ensure data types are correct (numbers for marks, text for names)
4. Check for empty required fields
5. Verify Result Type and Subject Result values

For technical support, contact the system administrator.
