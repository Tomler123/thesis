const daysTag = document.querySelector(".days"),
currentDate = document.querySelector(".current-date"),
prevNextIcon = document.querySelectorAll(".icons span");

// getting new date, current year and month
let date = new Date(),
currYear = date.getFullYear(),
currMonth = date.getMonth();

// storing full name of all months in array
const months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];
let highlightedDates = []; // This will hold your highlighted dates after fetching from the server

// After entering the page, colors will be displayed correctly
fetchSubscriptionStatusByDay().then(statusByDay => {
    renderCalendar(highlightedDates, statusByDay);
});

const renderCalendar = (highlightedDates = [], statusByDay = {}) => {
    let firstDayofMonth = new Date(currYear, currMonth, 1).getDay(), // getting first day of month
    lastDateofMonth = new Date(currYear, currMonth + 1, 0).getDate(), // getting last date of month
    lastDayofMonth = new Date(currYear, currMonth, lastDateofMonth).getDay(), // getting last day of month
    lastDateofLastMonth = new Date(currYear, currMonth, 0).getDate(); // getting last date of previous month
    let liTag = "";

    for (let i = firstDayofMonth; i > 0; i--) { // creating li of previous month last days
        liTag += `<li class="inactive">${lastDateofLastMonth - i + 1}</li>`;
    }

    for (let i = 1; i <= lastDateofMonth; i++) { // creating li of all days of current month
        // adding active class to li if the current day, month, and year matched
        let isToday = i === date.getDate() && currMonth === new Date().getMonth() 
                     && currYear === new Date().getFullYear() ? "active" : "";
        let isHighlighted = highlightedDates.includes(i) ? "highlighted" : "";
        // liTag += `<li class="${isToday} ${isHighlighted}">${i}</li>`;
        let isAllFulfilled = statusByDay[i] ? "all-fulfilled" : "";
        liTag += `<li class="${isToday} ${isHighlighted} ${isAllFulfilled}">${i}</li>`;
    }

    for (let i = lastDayofMonth; i < 6; i++) { // creating li of next month first days
        liTag += `<li class="inactive">${i - lastDayofMonth + 1}</li>`
    }
    currentDate.innerText = `${months[currMonth]} ${currYear}`; // passing current mon and yr as currentDate text
    daysTag.innerHTML = liTag;
    document.querySelectorAll('.highlighted').forEach(day => {
        day.addEventListener('click', function(event) {
            // Stops the click from propagating to the document level
            event.stopPropagation(); 
            getSubscriptions(this.textContent).then(subscriptions => {
                updateSubscriptionDetails(subscriptions);
                const detailsElement = document.querySelector('.subscription-details');
                detailsElement.innerHTML = subscriptions.map(sub => `${sub.name} - Amount: ${sub.amount}`).join('<br>');
                detailsElement.style.display = 'block';
            });

            
        });

        document.addEventListener('click', function(event) {
            const detailsElement = document.querySelector('.subscription-details');
            if (!detailsElement.contains(event.target)) {
                detailsElement.style.display = 'none';
            }
        });
    });
    document.querySelectorAll('.status-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const subscriptionId = this.id.replace('sub', ''); // Correctly extract subscription ID
            const isFulfilled = this.checked; // Boolean value true or false
            fetch('/update_subscription_status', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
              },
              body: JSON.stringify({
                sub_id: subscriptionId,
                status: isFulfilled
              })
            })
            .then(response => response.json())
            .then(data => console.log(data))
            .catch(error => console.error('Error:', error));
          });
      });
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const wrap = document.querySelector('.wrap');
        const highlightedDates = JSON.parse(wrap.getAttribute('data-subscription-dates'));
        renderCalendar(highlightedDates);
    });
} else {
    const wrap = document.querySelector('.wrap');
    const highlightedDates = JSON.parse(wrap.getAttribute('data-subscription-dates'));
    renderCalendar(highlightedDates);
}
renderCalendar(highlightedDates);

document.addEventListener('click', function(event) {
    const detailsElement = document.querySelector('.subscription-details');
    const clickInsideDetails = detailsElement.contains(event.target);
    const clickOnHighlightedDay = event.target.classList.contains('highlighted');
  
    if (!clickInsideDetails && !clickOnHighlightedDay) {
      detailsElement.style.display = 'none';
    }
});

prevNextIcon.forEach(icon => { // getting prev and next icons
    icon.addEventListener("click", () => {
        // Log to check if the event is fired
        currMonth = icon.id === "prev" ? currMonth - 1 : currMonth + 1;
        if (currMonth < 0 || currMonth > 11) {
            date = new Date(currYear, currMonth);
            currYear = date.getFullYear();
            currMonth = date.getMonth();
        } else {
            date = new Date();
        }
        fetchSubscriptionStatusByDay().then(statusByDay => {
            renderCalendar(highlightedDates, statusByDay);
        });
        // renderCalendar(highlightedDates); // Call renderCalendar with highlightedDates
    });
});

// Mock function to simulate fetching subscription data
// Replace this with actual fetching logic from your server
function getSubscriptions(day) {
    return fetch('/get_subscriptions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        },
        body: JSON.stringify({day: day})
    })
    .then(response => response.json())
    .then(subscriptions => {
        updateSubscriptionDetails(subscriptions);
    });
}

function updateSubscriptionDetails(subscriptions) {
    const detailsElement = document.querySelector('.subscription-details');
    let content = subscriptions.map(sub => `
        <div class="subscription-item">
            <span>${sub.name} - Amount: ${sub.amount}</span>
            <input type="checkbox" class="status-checkbox" id="sub${sub.id}" ${sub.fulfilled ? 'checked' : ''}>
            <label for="sub${sub.id}"></label>
        </div>
    `).join('');

    detailsElement.innerHTML = content;
    detailsElement.style.display = 'block';

    // Now attach change event listeners to newly added checkboxes
    document.querySelectorAll('.status-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });
}

function handleCheckboxChange() {
    fetch('/update_subscription_status', {
        method: 'POST',
        body: JSON.stringify({
            sub_id: this.id.replace('sub', ''),
            status: this.checked
        }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
    .then(response => response.json())
    .then(data => console.log(data));
}
function fetchSubscriptionStatusByDay() {
    return fetch('/get_subscription_status_by_day', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
        }
    })
    .then(response => response.json());
}
document.addEventListener('DOMContentLoaded', () => {
    const wrap = document.querySelector('.wrap');
    highlightedDates = JSON.parse(wrap.getAttribute('data-subscription-dates') || '[]');
    renderCalendar(highlightedDates);
});