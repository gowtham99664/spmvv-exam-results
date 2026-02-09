import React, { useState } from 'react';
import { studentService } from '../services/resultsService';

const SemesterSummaryTable = ({ studentInfo, semesterSummary, onRefresh }) => {
  const [expandedSemester, setExpandedSemester] = useState(null);
  const [subjectDetails, setSubjectDetails] = useState({});
  const [loading, setLoading] = useState({});
  const [editingSubject, setEditingSubject] = useState(null);

  const toggleSemester = async (resultId) => {
    if (expandedSemester === resultId) {
      setExpandedSemester(null);
      return;
    }

    setExpandedSemester(resultId);

    // Fetch subject details if not already loaded
    if (!subjectDetails[resultId]) {
      setLoading({ ...loading, [resultId]: true });
      try {
        const data = await studentService.getSemesterSubjects(resultId);
        setSubjectDetails({ ...subjectDetails, [resultId]: data.subjects });
      } catch (error) {
        console.error('Error fetching subject details:', error);
        alert('Failed to load subject details');
      } finally {
        setLoading({ ...loading, [resultId]: false });
      }
    }
  };

  const handleEditClick = (subject) => {
    setEditingSubject(subject);
  };

  const handleUpdateSuccess = () => {
    setEditingSubject(null);
    // Refresh subject details
    if (expandedSemester) {
      const resultId = expandedSemester;
      setLoading({ ...loading, [resultId]: true });
      studentService.getSemesterSubjects(resultId)
        .then(data => {
          setSubjectDetails({ ...subjectDetails, [resultId]: data.subjects });
        })
        .catch(error => {
          console.error('Error refreshing subject details:', error);
        })
        .finally(() => {
          setLoading({ ...loading, [resultId]: false });
        });
    }
    // Also refresh the parent
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <div className="card mb-4">
      <div className="card-header">
        <h5 className="mb-0">Student Results History</h5>
        {studentInfo && (
          <div className="mt-2">
            <strong>Roll Number:</strong> {studentInfo.roll_number} | 
            <strong> Name:</strong> {studentInfo.student_name} | 
            <strong> Course:</strong> {studentInfo.course} | 
            <strong> Branch:</strong> {studentInfo.branch}
          </div>
        )}
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-bordered table-hover">
            <thead className="table-light">
              <tr>
                <th>Year</th>
                <th>Semester</th>
                <th>Exam Name</th>
                <th>Total %</th>
                <th>Result</th>
                <th>Pending Subjects</th>
                <th>Number of Attempts</th>
                <th>Completion Month/Year</th>
                <th>Uploaded At</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {semesterSummary && semesterSummary.length > 0 ? (
                semesterSummary.map((semester) => (
                  <React.Fragment key={semester.result_id}>
                    <tr>
                      <td>{semester.year}</td>
                      <td>{semester.semester}</td>
                      <td>{semester.exam_name}</td>
                      <td>{semester.total_marks_percentage ? semester.total_marks_percentage.toFixed(2) + '%' : 'N/A'}</td>
                      <td>
                        <span className={`badge ${semester.overall_result === 'Pass' ? 'bg-success' : 'bg-danger'}`}>
                          {semester.overall_result}
                        </span>
                      </td>
                      <td>{semester.pending_subjects}</td>
                      <td>{semester.max_attempts}</td>
                      <td>
                        {semester.completion_date ? (
                          <span className="badge bg-success">
                            {new Date(semester.completion_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                          </span>
                        ) : (
                          <span className="text-muted">-</span>
                        )}
                      </td>
                      <td>{new Date(semester.uploaded_at).toLocaleString()}</td>
                      <td>
                        <button
                          className="btn btn-sm btn-primary"
                          onClick={() => toggleSemester(semester.result_id)}
                        >
                          {expandedSemester === semester.result_id ? 'Hide Details' : 'View Details'}
                        </button>
                      </td>
                    </tr>
                    {expandedSemester === semester.result_id && (
                      <tr>
                        <td colSpan="10">
                          {loading[semester.result_id] ? (
                            <div className="text-center p-3">
                              <div className="spinner-border" role="status">
                                <span className="visually-hidden">Loading...</span>
                              </div>
                            </div>
                          ) : subjectDetails[semester.result_id] ? (
                            <div className="p-3">
                              <h6>Subject-wise Details</h6>
                              <table className="table table-sm table-bordered">
                                <thead className="table-secondary">
                                  <tr>
                                    <th>Subject Code</th>
                                    <th>Subject Name</th>
                                    <th>Internal</th>
                                    <th>External</th>
                                    <th>Total</th>
                                    <th>Result</th>
                                    <th>Grade</th>
                                    <th>Attempts</th>
                                    <th>Action</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {subjectDetails[semester.result_id].map((subject) => (
                                    <tr key={subject.id}>
                                      <td>{subject.subject_code}</td>
                                      <td>{subject.subject_name}</td>
                                      <td>{subject.internal_marks !== null ? subject.internal_marks : 'N/A'}</td>
                                      <td>{subject.external_marks !== null ? subject.external_marks : 'N/A'}</td>
                                      <td>{subject.total_marks !== null ? subject.total_marks : 'N/A'}</td>
                                      <td>
                                        <span className={`badge ${
                                          subject.subject_result === 'pass' ? 'bg-success' :
                                          subject.subject_result === 'fail' ? 'bg-danger' : 'bg-secondary'
                                        }`}>
                                          {subject.subject_result}
                                        </span>
                                      </td>
                                      <td>{subject.grade || 'N/A'}</td>
                                      <td>
                                        <span className="badge bg-info">{subject.attempts}</span>
                                      </td>
                                      <td>
                                        <button
                                          className="btn btn-sm btn-warning"
                                          onClick={() => handleEditClick(subject)}
                                        >
                                          Edit
                                        </button>
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ) : (
                            <div className="p-3 text-center">No subject details available</div>
                          )}
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan="10" className="text-center">No semester data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {editingSubject && (
        <UpdateMarksModal
          subject={editingSubject}
          onClose={() => setEditingSubject(null)}
          onSuccess={handleUpdateSuccess}
        />
      )}
    </div>
  );
};

const UpdateMarksModal = ({ subject, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    internal_marks: subject.internal_marks || 0,
    external_marks: subject.external_marks || 0,
    total_marks: subject.total_marks || 0,
    subject_result: subject.subject_result || 'fail',
    grade: subject.grade || ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      const updated = { ...prev, [name]: value };
      
      // Auto-calculate total marks if internal or external changes
      if (name === 'internal_marks' || name === 'external_marks') {
        const internal = parseInt(name === 'internal_marks' ? value : prev.internal_marks) || 0;
        const external = parseInt(name === 'external_marks' ? value : prev.external_marks) || 0;
        updated.total_marks = internal + external;
      }
      
      return updated;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await studentService.updateSubjectMarks(subject.id, formData);
      alert('Marks updated successfully!');
      onSuccess();
    } catch (err) {
      console.error('Error updating marks:', err);
      setError(err.response?.data?.error || 'Failed to update marks');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Update Subject Marks</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}
              
              <div className="mb-3">
                <strong>Subject:</strong> {subject.subject_code} - {subject.subject_name}
              </div>
              <div className="mb-3">
                <strong>Current Attempts:</strong> {subject.attempts}
              </div>

              <div className="mb-3">
                <label className="form-label">Internal Marks</label>
                <input
                  type="number"
                  className="form-control"
                  name="internal_marks"
                  value={formData.internal_marks}
                  onChange={handleChange}
                  min="0"
                  max="100"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">External Marks</label>
                <input
                  type="number"
                  className="form-control"
                  name="external_marks"
                  value={formData.external_marks}
                  onChange={handleChange}
                  min="0"
                  max="100"
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Total Marks (Auto-calculated)</label>
                <input
                  type="number"
                  className="form-control"
                  name="total_marks"
                  value={formData.total_marks}
                  readOnly
                  disabled
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Result</label>
                <select
                  className="form-select"
                  name="subject_result"
                  value={formData.subject_result}
                  onChange={handleChange}
                >
                  <option value="pass">Pass</option>
                  <option value="fail">Fail</option>
                  <option value="absent">Absent</option>
                </select>
              </div>

              <div className="mb-3">
                <label className="form-label">Grade</label>
                <input
                  type="text"
                  className="form-control"
                  name="grade"
                  value={formData.grade}
                  onChange={handleChange}
                  maxLength="10"
                />
              </div>

              <div className="alert alert-info">
                <small>
                  <strong>Note:</strong> If you change the result from 'fail' to 'pass', 
                  the attempt count will automatically increment.
                </small>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={submitting}>
                {submitting ? 'Updating...' : 'Update Marks'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SemesterSummaryTable;
