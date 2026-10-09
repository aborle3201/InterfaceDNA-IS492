window.RUN = {
  "meta": {
    "product": "InterfaceDNA",
    "institution": "Demo University",
    "scenario_type": "synthetic",
    "term": "Fall 2026",
    "disclaimer": "All student records, policies, dates, offices, and system responses in this prototype are fictional and exist only to demonstrate the interaction model."
  },
  "students": {
    "alex": {
      "name": "Alex Morgan",
      "persona": "Enrollment-sensitive student",
      "major": "Computer Science",
      "catalogYear": "2024-2025",
      "currentCredits": 16,
      "completedCredits": 76,
      "gpa": 3.42,
      "courses": [
        {"code":"CS 411","title":"Computer Systems","credits":4,"status":"Enrolled","requirement":"Major required"},
        {"code":"CS 425","title":"Distributed Systems","credits":4,"status":"Enrolled","requirement":"Major elective"},
        {"code":"STAT 400","title":"Statistics","credits":4,"status":"Enrolled","requirement":"Technical elective"},
        {"code":"ART 105","title":"Design Foundations","credits":4,"status":"Enrolled","requirement":"General education"}
      ],
      "constraints": ["Maintain at least 12 enrolled credits for full-time status"],
      "holds": []
    },
    "maya": {
      "name": "Maya Patel",
      "persona": "Graduating senior",
      "major": "Information Sciences",
      "catalogYear": "2023-2024",
      "currentCredits": 12,
      "completedCredits": 112,
      "gpa": 3.68,
      "courses": [
        {"code":"IS 492","title":"Technology Entrepreneurship","credits":4,"status":"Enrolled","requirement":"Capstone"},
        {"code":"IS 455","title":"Data Visualization","credits":4,"status":"Enrolled","requirement":"Major elective"},
        {"code":"STAT 385","title":"Statistics Programming","credits":4,"status":"Enrolled","requirement":"Supporting coursework"}
      ],
      "graduation": {
        "totalRequired": 120,
        "completed": 112,
        "inProgress": 12,
        "requirements": [
          {"name":"University minimum credits","status":"In progress","detail":"112 completed + 12 in progress"},
          {"name":"Capstone","status":"In progress","detail":"IS 492 currently enrolled"},
          {"name":"Major electives","status":"Satisfied","detail":"Requirement met if current coursework is completed"},
          {"name":"Residency requirement","status":"Satisfied","detail":"Verified from degree audit"}
        ]
      },
      "holds": []
    },
    "jordan": {
      "name": "Jordan Lee",
      "persona": "Student with registration hold",
      "major": "Computer Engineering",
      "catalogYear": "2025-2026",
      "currentCredits": 14,
      "completedCredits": 54,
      "gpa": 3.21,
      "courses": [],
      "holds": [
        {"type":"Advising hold","office":"Academic Advising","reason":"Required semester planning check-in","status":"Action needed","canRequest":true},
        {"type":"Student account hold","office":"Student Accounts","reason":"Outstanding account review","status":"Action needed","canRequest":false}
      ]
    }
  },
  "policies": {
    "courseDrop": {
      "title": "Course Enrollment & Drop Policy",
      "source": "Demo University Academic Regulations",
      "version": "2026.09",
      "approved": true,
      "urlLabel": "Academic Regulations → Enrollment → Course Drops",
      "deadline": "September 30, 2026",
      "threshold": 12,
      "notes": [
        "Students must review academic and enrollment consequences before submitting a course-drop request.",
        "A student dropping below the full-time threshold should review any consequences tied to enrollment status.",
        "The student must explicitly confirm a consequential action before submission."
      ]
    },
    "courseDropConflict": {
      "sourceA": {"title":"Academic Calendar PDF","date":"September 25, 2026","version":"2026.08"},
      "sourceB": {"title":"Academic Regulations","date":"September 30, 2026","version":"2026.09"}
    },
    "graduation": {
      "title": "Bachelor's Degree Requirements",
      "source": "Demo University Undergraduate Catalog",
      "version": "2026.1",
      "approved": true,
      "urlLabel": "Catalog → Degree Requirements"
    },
    "registration": {
      "title": "Registration Holds & Clearance",
      "source": "Demo University Registrar",
      "version": "2026.2",
      "approved": true,
      "urlLabel": "Registrar → Registration Holds"
    }
  },
  "offices": {
    "registrar": {"name":"Office of the Registrar","purpose":"Enrollment records, course deadlines, registration processing"},
    "advising": {"name":"Academic Advising","purpose":"Degree planning and advising holds"},
    "accounts": {"name":"Student Accounts","purpose":"Financial/account holds and account review"}
  }
}
;
