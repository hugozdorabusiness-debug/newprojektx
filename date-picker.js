// Enhanced Date Wheel Picker with 3D Effects
class DateWheelPicker {
    constructor() {
        this.selectedDate = new Date();
        this.selectedDay = this.selectedDate.getDate();
        this.selectedMonth = this.selectedDate.getMonth();
        this.selectedYear = this.selectedDate.getFullYear();

        this.ITEM_HEIGHT = 50;
        this.VISIBLE_ITEMS = 5;
        this.PERSPECTIVE_ORIGIN = this.ITEM_HEIGHT * 2;

        this.months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];

        this.wheels = {
            day: { currentY: 0, targetY: 0, isDragging: false, startY: 0 },
            month: { currentY: 0, targetY: 0, isDragging: false, startY: 0 },
            year: { currentY: 0, targetY: 0, isDragging: false, startY: 0 }
        };

        this.init();
    }

    init() {
        this.createPickerHTML();
        this.setupEventListeners();
        this.startAnimationLoop();
    }

    createPickerHTML() {
        const overlay = document.createElement('div');
        overlay.className = 'date-picker-overlay';
        overlay.id = 'datePickerOverlay';

        const container = document.createElement('div');
        container.className = 'date-picker-container';
        container.id = 'datePickerContainer';

        container.innerHTML = `
            <div class="date-picker-header">
                <h3 class="date-picker-title">Select Date</h3>
                <button class="date-picker-close" id="datePickerClose">✕</button>
            </div>
            
            <div class="date-picker-wheels-container">
                <div class="date-picker-wheels">
                    <div class="wheel-wrapper">
                        <div class="date-wheel-label">Day</div>
                        <div class="date-wheel" id="dayWheel" data-wheel="day">
                            <div class="date-wheel-gradient top"></div>
                            <div class="date-wheel-highlight"></div>
                            <div class="date-wheel-gradient bottom"></div>
                            <div class="date-wheel-items" id="dayWheelItems"></div>
                        </div>
                    </div>
                    
                    <div class="wheel-wrapper">
                        <div class="date-wheel-label">Month</div>
                        <div class="date-wheel" id="monthWheel" data-wheel="month">
                            <div class="date-wheel-gradient top"></div>
                            <div class="date-wheel-highlight"></div>
                            <div class="date-wheel-gradient bottom"></div>
                            <div class="date-wheel-items" id="monthWheelItems"></div>
                        </div>
                    </div>
                    
                    <div class="wheel-wrapper">
                        <div class="date-wheel-label">Year</div>
                        <div class="date-wheel" id="yearWheel" data-wheel="year">
                            <div class="date-wheel-gradient top"></div>
                            <div class="date-wheel-highlight"></div>
                            <div class="date-wheel-gradient bottom"></div>
                            <div class="date-wheel-items" id="yearWheelItems"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="date-picker-actions">
                <button class="date-picker-btn date-picker-btn-cancel" id="datePickerCancel">Cancel</button>
                <button class="date-picker-btn date-picker-btn-confirm" id="datePickerConfirm">Confirm</button>
            </div>
        `;

        document.body.appendChild(overlay);
        document.body.appendChild(container);

        this.populateWheels();
    }

    populateWheels() {
        // Populate days (1-31)
        const dayItems = document.getElementById('dayWheelItems');
        const daysInMonth = this.getDaysInMonth(this.selectedYear, this.selectedMonth);
        for (let i = 1; i <= daysInMonth; i++) {
            const item = document.createElement('div');
            item.className = 'date-wheel-item';
            item.textContent = i;
            item.dataset.value = i;
            item.dataset.index = i - 1;
            dayItems.appendChild(item);
        }

        // Populate months
        const monthItems = document.getElementById('monthWheelItems');
        this.months.forEach((month, index) => {
            const item = document.createElement('div');
            item.className = 'date-wheel-item';
            item.textContent = month;
            item.dataset.value = index;
            item.dataset.index = index;
            monthItems.appendChild(item);
        });

        // Populate years (current year - 10 to current year + 10)
        const yearItems = document.getElementById('yearWheelItems');
        const currentYear = new Date().getFullYear();
        for (let i = currentYear + 10; i >= currentYear - 10; i--) {
            const item = document.createElement('div');
            item.className = 'date-wheel-item';
            item.textContent = i;
            item.dataset.value = i;
            item.dataset.index = currentYear + 10 - i;
            yearItems.appendChild(item);
        }

        this.scrollToSelected();
    }

    getDaysInMonth(year, month) {
        return new Date(year, month + 1, 0).getDate();
    }

    scrollToSelected() {
        const centerOffset = Math.floor(this.VISIBLE_ITEMS / 2) * this.ITEM_HEIGHT;

        // Day
        this.wheels.day.targetY = -(this.selectedDay - 1) * this.ITEM_HEIGHT;
        this.wheels.day.currentY = this.wheels.day.targetY;

        // Month
        this.wheels.month.targetY = -this.selectedMonth * this.ITEM_HEIGHT;
        this.wheels.month.currentY = this.wheels.month.targetY;

        // Year
        const currentYear = new Date().getFullYear();
        const yearIndex = currentYear + 10 - this.selectedYear;
        this.wheels.year.targetY = -yearIndex * this.ITEM_HEIGHT;
        this.wheels.year.currentY = this.wheels.year.targetY;

        this.updateWheelPositions();
    }

    setupEventListeners() {
        const overlay = document.getElementById('datePickerOverlay');
        const closeBtn = document.getElementById('datePickerClose');
        const cancelBtn = document.getElementById('datePickerCancel');
        const confirmBtn = document.getElementById('datePickerConfirm');

        overlay.addEventListener('click', () => this.close());
        closeBtn.addEventListener('click', () => this.close());
        cancelBtn.addEventListener('click', () => this.close());
        confirmBtn.addEventListener('click', () => this.confirm());

        // Setup drag for each wheel
        ['day', 'month', 'year'].forEach(type => {
            const wheel = document.getElementById(`${type}Wheel`);
            this.setupWheelDrag(wheel, type);
            this.setupWheelScroll(wheel, type);
        });
    }

    setupWheelDrag(wheel, type) {
        let startY = 0;
        let startScrollY = 0;

        const onStart = (e) => {
            this.wheels[type].isDragging = true;
            startY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            startScrollY = this.wheels[type].currentY;
            wheel.style.cursor = 'grabbing';
        };

        const onMove = (e) => {
            if (!this.wheels[type].isDragging) return;
            e.preventDefault();

            const currentY = e.type.includes('mouse') ? e.clientY : e.touches[0].clientY;
            const deltaY = currentY - startY;
            this.wheels[type].currentY = startScrollY + deltaY;
            this.wheels[type].targetY = this.wheels[type].currentY;
        };

        const onEnd = () => {
            if (!this.wheels[type].isDragging) return;
            this.wheels[type].isDragging = false;
            wheel.style.cursor = 'grab';
            this.snapToNearest(type);
        };

        wheel.addEventListener('mousedown', onStart);
        wheel.addEventListener('touchstart', onStart, { passive: false });

        document.addEventListener('mousemove', onMove);
        document.addEventListener('touchmove', onMove, { passive: false });

        document.addEventListener('mouseup', onEnd);
        document.addEventListener('touchend', onEnd);
    }

    setupWheelScroll(wheel, type) {
        wheel.addEventListener('wheel', (e) => {
            e.preventDefault();
            const direction = e.deltaY > 0 ? 1 : -1;

            const items = wheel.querySelectorAll('.date-wheel-item');
            const currentIndex = Math.round(-this.wheels[type].targetY / this.ITEM_HEIGHT);
            const newIndex = Math.max(0, Math.min(items.length - 1, currentIndex + direction));

            this.wheels[type].targetY = -newIndex * this.ITEM_HEIGHT;
            this.updateSelection(type, newIndex);
        }, { passive: false });
    }

    snapToNearest(type) {
        const items = document.getElementById(`${type}WheelItems`).children;
        const currentIndex = Math.round(-this.wheels[type].currentY / this.ITEM_HEIGHT);
        const clampedIndex = Math.max(0, Math.min(items.length - 1, currentIndex));

        this.wheels[type].targetY = -clampedIndex * this.ITEM_HEIGHT;
        this.updateSelection(type, clampedIndex);
    }

    updateSelection(type, index) {
        if (type === 'day') {
            this.selectedDay = index + 1;
        } else if (type === 'month') {
            this.selectedMonth = index;
            // Update days if month changed
            this.updateDaysInMonth();
        } else if (type === 'year') {
            const currentYear = new Date().getFullYear();
            this.selectedYear = currentYear + 10 - index;
            // Update days if year changed (leap year)
            this.updateDaysInMonth();
        }
    }

    updateDaysInMonth() {
        const daysInMonth = this.getDaysInMonth(this.selectedYear, this.selectedMonth);
        const dayItems = document.getElementById('dayWheelItems');
        const currentDays = dayItems.children.length;

        if (currentDays !== daysInMonth) {
            dayItems.innerHTML = '';
            for (let i = 1; i <= daysInMonth; i++) {
                const item = document.createElement('div');
                item.className = 'date-wheel-item';
                item.textContent = i;
                item.dataset.value = i;
                item.dataset.index = i - 1;
                dayItems.appendChild(item);
            }

            // Adjust selected day if needed
            if (this.selectedDay > daysInMonth) {
                this.selectedDay = daysInMonth;
                this.wheels.day.targetY = -(this.selectedDay - 1) * this.ITEM_HEIGHT;
            }
        }
    }

    startAnimationLoop() {
        const animate = () => {
            ['day', 'month', 'year'].forEach(type => {
                if (!this.wheels[type].isDragging) {
                    // Smooth spring animation
                    const diff = this.wheels[type].targetY - this.wheels[type].currentY;
                    this.wheels[type].currentY += diff * 0.2;
                }
            });

            this.updateWheelPositions();
            requestAnimationFrame(animate);
        };
        animate();
    }

    updateWheelPositions() {
        ['day', 'month', 'year'].forEach(type => {
            const items = document.getElementById(`${type}WheelItems`);
            if (!items) return;

            const centerOffset = Math.floor(this.VISIBLE_ITEMS / 2) * this.ITEM_HEIGHT;
            items.style.transform = `translateY(${this.wheels[type].currentY + centerOffset}px)`;

            // Update 3D transforms for each item
            Array.from(items.children).forEach((item, index) => {
                const itemY = index * this.ITEM_HEIGHT + this.wheels[type].currentY + centerOffset;
                const distance = Math.abs(itemY - centerOffset);
                const maxDistance = this.ITEM_HEIGHT * 2;

                const rotateX = ((itemY - centerOffset) / maxDistance) * 45;
                const scale = Math.max(0.7, 1 - (distance / maxDistance) * 0.3);
                const opacity = Math.max(0.3, 1 - (distance / maxDistance) * 0.7);

                const isSelected = Math.abs(itemY - centerOffset) < this.ITEM_HEIGHT / 2;

                item.style.transform = `
                    rotateX(${rotateX}deg) 
                    scale(${scale})
                    translateZ(${isSelected ? '20px' : '0px'})
                `;
                item.style.opacity = opacity;
                item.classList.toggle('selected', isSelected);
            });
        });
    }

    open() {
        document.getElementById('datePickerOverlay').classList.add('active');
        document.getElementById('datePickerContainer').classList.add('active');
        this.scrollToSelected();
    }

    close() {
        document.getElementById('datePickerOverlay').classList.remove('active');
        document.getElementById('datePickerContainer').classList.remove('active');
    }

    confirm() {
        const selectedDate = new Date(this.selectedYear, this.selectedMonth, this.selectedDay);

        const event = new CustomEvent('dateSelected', {
            detail: {
                date: selectedDate,
                formatted: selectedDate.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                })
            }
        });
        document.dispatchEvent(event);

        if (typeof showToast === 'function') {
            showToast(`Date selected: ${event.detail.formatted}`, 'success');
        }
        this.close();
    }
}

// Initialize date picker
let datePicker;
document.addEventListener('DOMContentLoaded', () => {
    datePicker = new DateWheelPicker();
});

// Make it globally accessible
window.openDatePicker = () => {
    if (datePicker) {
        datePicker.open();
    }
};
