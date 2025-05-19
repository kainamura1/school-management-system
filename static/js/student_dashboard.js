// Student Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Access the data passed from Django
    const data = window.dashboardData || {};
    
    // Calculate assignment progress percentage
    updateAssignmentProgress(data.progress);
    
    // Initialize dashboard components
    initializeCalendar(data);
    populateAchievements(data);
    populateActivityTimeline(data);
});

function updateAssignmentProgress(progressData) {
    const assignmentProgressBar = document.getElementById('assignmentProgressBar');
    if (assignmentProgressBar) {
        const completed = progressData.assignmentsCompleted || 0;
        const total = progressData.totalAssignments || 0;
        const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
        
        assignmentProgressBar.style.width = `${percentage}%`;
        assignmentProgressBar.setAttribute('aria-valuenow', percentage);
        
        // Update overall progress bar too
        const overallProgressBar = document.querySelector('.progress-bar.bg-success');
        if (overallProgressBar) {
            const overallPercentage = progressData.semesterCompletion || 0;
            overallProgressBar.style.width = `${overallPercentage}%`;
            overallProgressBar.setAttribute('aria-valuenow', overallPercentage);
            
            // Update text display
            const overallProgressText = document.getElementById('overallProgress');
            if (overallProgressText) {
                overallProgressText.textContent = `${overallPercentage}%`;
            }
        }
    }
}

function initializeCalendar(data) {
    const today = new Date();
    let currentMonth = today.getMonth();
    let currentYear = today.getFullYear();
    
    // Display current month
    updateCalendar(currentMonth, currentYear, data);
    
    // Add event listeners for month navigation
    const prevMonthBtn = document.getElementById('prevMonth');
    const nextMonthBtn = document.getElementById('nextMonth');
    
    if (prevMonthBtn) {
        prevMonthBtn.addEventListener('click', function() {
            currentMonth--;
            if (currentMonth < 0) {
                currentMonth = 11;
                currentYear--;
            }
            updateCalendar(currentMonth, currentYear, data);
        });
    }
    
    if (nextMonthBtn) {
        nextMonthBtn.addEventListener('click', function() {
            currentMonth++;
            if (currentMonth > 11) {
                currentMonth = 0;
                currentYear++;
            }
            updateCalendar(currentMonth, currentYear, data);
        });
    }
}

function updateCalendar(month, year, data) {
    const monthNames = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"];
    
    // Update month/year display
    const currentMonthEl = document.getElementById('currentMonth');
    if (currentMonthEl) {
        currentMonthEl.textContent = `${monthNames[month]} ${year}`;
    }
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    // Generate calendar
    const calendarDays = document.getElementById('calendarDays');
    if (!calendarDays) return;
    
    calendarDays.innerHTML = '';
    
    // Add empty cells for days before start of month
    for (let i = 0; i < firstDay; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day empty';
        calendarDays.appendChild(emptyDay);
    }
    
    // Create event map for this month
    const eventDays = getEventDaysForMonth(month, year, data);
    
    // Add days of the month
    const today = new Date();
    const currentDate = today.getDate();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    for (let i = 1; i <= daysInMonth; i++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        dayElement.textContent = i;
        
        // Highlight today
        if (i === currentDate && month === currentMonth && year === currentYear) {
            dayElement.classList.add('today');
        }
        
        // Add event dots
        if (eventDays.has(i)) {
            const dot = document.createElement('span');
            dot.className = 'event-dot';
            dayElement.appendChild(dot);
            
            // Add tooltip
            dayElement.setAttribute('data-bs-toggle', 'tooltip');
            dayElement.setAttribute('data-bs-placement', 'top');
            dayElement.setAttribute('title', 'You have events on this day');
        }
        
        calendarDays.appendChild(dayElement);
    }
    
    // Update upcoming events
    updateUpcomingEvents(data, month, year);
}

function getEventDaysForMonth(month, year, data) {
    const eventDays = new Set();
    
    // Add assignment submission dates
    if (data.assignments && data.assignments.length) {
        data.assignments.forEach(assignment => {
            const date = new Date(assignment.submittedDate);
            if (date.getMonth() === month && date.getFullYear() === year) {
                eventDays.add(date.getDate());
            }
        });
    }
    
    // Add announcement dates
    if (data.announcements && data.announcements.length) {
        data.announcements.forEach(announcement => {
            const date = new Date(announcement.date);
            if (date.getMonth() === month && date.getFullYear() === year) {
                eventDays.add(date.getDate());
            }
        });
    }
    
    return eventDays;
}

function updateUpcomingEvents(data, month, year) {
    const upcomingEventsContainer = document.getElementById('upcomingEvents');
    if (!upcomingEventsContainer) return;
    
    let events = [];
    
    // Add upcoming assignment events (due dates)
    if (data.assignments && data.assignments.length) {
        data.assignments.forEach(assignment => {
            const submittedDate = new Date(assignment.submittedDate);
            // Only show recent submissions (last 2 weeks)
            const twoWeeksAgo = new Date();
            twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
            
            if (submittedDate >= twoWeeksAgo) {
                events.push({
                    date: submittedDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
                    title: `Assignment: ${assignment.title}`,
                    time: 'Submitted',
                    location: assignment.course,
                    type: 'assignment'
                });
            }
        });
    }
    
    // Add announcement events
    if (data.announcements && data.announcements.length) {
        data.announcements.slice(0, 3).forEach(announcement => {
            const announcementDate = new Date(announcement.date);
            events.push({
                date: announcementDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
                title: `Announcement: ${announcement.title}`,
                time: 'Posted',
                location: announcement.course,
                type: 'announcement'
            });
        });
    }
    
    // Sort events by date (newest first)
    events.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    // Take only the 5 most recent events
    events = events.slice(0, 5);
    
    upcomingEventsContainer.innerHTML = '';
    
    if (events.length > 0) {
        events.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = 'event-item';
            eventElement.innerHTML = `
                <div class="event-date">${event.date}</div>
                <div class="event-details">
                    <h6>${event.title}</h6>
                    <div class="event-info">
                        <span><i class="far fa-clock me-1"></i>${event.time}</span>
                        <span><i class="fas fa-map-marker-alt me-1"></i>${event.location}</span>
                    </div>
                </div>
            `;
            upcomingEventsContainer.appendChild(eventElement);
        });
    } else {
        upcomingEventsContainer.innerHTML = '<div class="alert alert-info">No upcoming events scheduled.</div>';
    }
}

function populateAchievements(data) {
    const achievementsList = document.getElementById('achievementsList');
    if (!achievementsList) return;
    
    let achievements = [];
    
    // Generate dynamic achievements based on real data
    if (data.progress && data.progress.assignmentsCompleted > 0) {
        achievements.push({
            title: 'Assignment Submission',
            description: `You've completed ${data.progress.assignmentsCompleted} assignments this semester!`,
            date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
            icon: 'fas fa-tasks'
        });
    }
    
    if (data.courses && data.courses.length >= 3) {
        achievements.push({
            title: 'Course Explorer',
            description: `You're enrolled in ${data.courses.length} courses this semester`,
            date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
            icon: 'fas fa-book'
        });
    }
    
    // Always add one achievement if none exist
    if (achievements.length === 0) {
        achievements.push({
            title: 'Getting Started',
            description: 'You have successfully logged into the Student Management System!',
            date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
            icon: 'fas fa-star'
        });
    }
    
    achievementsList.innerHTML = '';
    
    achievements.forEach(achievement => {
        const achievementElement = document.createElement('div');
        achievementElement.className = 'achievement-item';
        achievementElement.innerHTML = `
            <div class="achievement-icon">
                <i class="${achievement.icon}"></i>
            </div>
            <div class="achievement-details">
                <h6>${achievement.title}</h6>
                <p>${achievement.description}</p>
                <small class="text-muted">${achievement.date}</small>
            </div>
        `;
        achievementsList.appendChild(achievementElement);
    });
}

function populateActivityTimeline(data) {
    const timelineContainer = document.getElementById('activityTimeline');
    if (!timelineContainer) return;
    
    let activities = [];
    
    // Add assignment activities
    if (data.assignments && data.assignments.length) {
        data.assignments.forEach(assignment => {
            const submittedDate = new Date(assignment.submittedDate);
            const today = new Date();
            const diffTime = Math.abs(today - submittedDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            let timeAgo;
            if (diffDays === 0) {
                timeAgo = "Today";
            } else if (diffDays === 1) {
                timeAgo = "Yesterday";
            } else if (diffDays < 7) {
                timeAgo = `${diffDays} days ago`;
            } else if (diffDays < 30) {
                timeAgo = `${Math.floor(diffDays / 7)} week(s) ago`;
            } else {
                timeAgo = `${Math.floor(diffDays / 30)} month(s) ago`;
            }
            
            activities.push({
                type: assignment.status === 'graded' ? 'grade' : 'assignment',
                title: assignment.status === 'graded' ? 'Received Grade' : 'Submitted Assignment',
                description: assignment.status === 'graded' ? 
                    `You received ${assignment.score}% on "${assignment.title}"` : 
                    `You submitted "${assignment.title}" for ${assignment.course}`,
                time: timeAgo,
                icon: assignment.status === 'graded' ? 'fas fa-check-circle' : 'fas fa-file-alt',
                date: submittedDate
            });
        });
    }
    
    // Add course enrollment activities
    if (data.courses && data.courses.length) {
        data.courses.forEach(course => {
            const enrollmentDate = new Date(course.enrollmentDate);
            // Only show recent enrollments (last month)
            const oneMonthAgo = new Date();
            oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
            
            if (enrollmentDate >= oneMonthAgo) {
                const today = new Date();
                const diffTime = Math.abs(today - enrollmentDate);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                
                let timeAgo;
                if (diffDays === 0) {
                    timeAgo = "Today";
                } else if (diffDays === 1) {
                    timeAgo = "Yesterday";
                } else if (diffDays < 7) {
                    timeAgo = `${diffDays} days ago`;
                } else if (diffDays < 30) {
                    timeAgo = `${Math.floor(diffDays / 7)} week(s) ago`;
                } else {
                    timeAgo = `${Math.floor(diffDays / 30)} month(s) ago`;
                }
                
                activities.push({
                    type: 'course',
                    title: 'Enrolled in Course',
                    description: `You enrolled in "${course.code} - ${course.title}"`,
                    time: timeAgo,
                    icon: 'fas fa-book',
                    date: enrollmentDate
                });
            }
        });
    }
    
    // Sort activities by date (newest first)
    activities.sort((a, b) => b.date - a.date);
    
    // Take only the 5 most recent activities
    activities = activities.slice(0, 5);
    
    timelineContainer.innerHTML = '';
    
    if (activities.length > 0) {
        activities.forEach((activity, index) => {
            const timelineItem = document.createElement('div');
            timelineItem.className = 'timeline-item';
            
            let iconClass = 'bg-primary';
            if (activity.type === 'grade') iconClass = 'bg-success';
            if (activity.type === 'assignment') iconClass = 'bg-warning';
            
            timelineItem.innerHTML = `
                <div class="timeline-icon ${iconClass}">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="timeline-content">
                    <h6>${activity.title}</h6>
                    <p>${activity.description}</p>
                    <small class="text-muted">${activity.time}</small>
                </div>
            `;
            timelineContainer.appendChild(timelineItem);
        });
    } else {
        timelineContainer.innerHTML = '<div class="alert alert-info">No recent activity to display.</div>';
    }
}
