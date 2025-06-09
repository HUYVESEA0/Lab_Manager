# Lab Manager - Design System
> Hệ thống thiết kế hoàn chỉnh cho ứng dụng quản lý phòng thí nghiệm Python Manager

## 🎨 Tổng Quan Design System

Lab Manager sử dụng một design system hiện đại với cảm hứng từ công nghệ giáo dục, tập trung vào trải nghiệm người dùng thân thiện và giao diện chuyên nghiệp.

---

## 🎯 Design Principles

### 1. **Educational First**
- Giao diện được thiết kế để hỗ trợ học tập và giảng dạy
- Sử dụng các màu sắc và typography giúp tập trung
- Layout rõ ràng, dễ điều hướng

### 2. **Modern & Professional**
- Aesthetic hiện đại với gradient và shadows tinh tế
- Typography sạch sẽ với font Roboto
- Responsive design cho mọi thiết bị

### 3. **User-Centric**
- Phân quyền rõ ràng (Student, Admin, System Administrator)
- Interface thích ứng theo vai trò người dùng
- Feedback và thông báo trực quan

---

## 🎨 Color Palette

### Primary Colors
```css
:root {
    --primary-color: #3a86ff;        /* Main brand color - Vibrant Blue */
    --secondary-color: #8338ec;      /* Accent color - Purple */
    --accent-color: #3a0ca3;         /* Deep accent - Dark Purple */
}
```

### Semantic Colors
```css
:root {
    --success-color: #38b000;        /* Success states - Green */
    --warning-color: #ffbe0b;        /* Warning states - Amber */
    --danger-color: #ff006e;         /* Error states - Pink */
}
```

### Neutral Colors
```css
:root {
    --light-bg: #f8f9fa;           /* Light background */
    --dark-bg: #212529;            /* Dark elements */
    --text-color: #343a40;         /* Primary text */
    --text-light: #f8f9fa;         /* Light text on dark */
}
```

### Usage Guidelines
- **Primary Blue**: Main actions, navigation, primary buttons
- **Secondary Purple**: Hover states, accents, secondary actions
- **Success Green**: Confirmations, positive feedback
- **Warning Amber**: Alerts, cautionary messages
- **Danger Pink**: Errors, destructive actions
- **Neutral Grays**: Text, backgrounds, subtle elements

---

## 📝 Typography

### Font Stack
```css
font-family: 'Roboto', sans-serif;
```

### Font Weights & Sizes
```css
/* Headings */
h1 { font-size: 2.5rem; font-weight: 700; }
h2 { font-size: 2rem; font-weight: 600; }
h3 { font-size: 1.75rem; font-weight: 600; }
h4 { font-size: 1.5rem; font-weight: 500; }
h5 { font-size: 1.25rem; font-weight: 500; }
h6 { font-size: 1rem; font-weight: 500; }

/* Body Text */
body { font-size: 1rem; line-height: 1.6; }
.text-small { font-size: 0.875rem; }
.text-large { font-size: 1.125rem; }
```

### Code Typography
```css
/* Code Elements */
pre, code, .code-block {
    font-family: 'Source Code Pro', 'Fira Code', monospace;
    background-color: #f7f7f9;
    border-radius: 4px;
    color: var(--accent-color);
}
```

---

## 🎭 Component System

### 1. **Navigation Components**

#### Main Navbar
```css
.navbar {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: none;
}
```

#### Dropdown Menus
- **Standard Dropdown**: User actions, navigation
- **Admin Dropdown**: Advanced features với color-coding
- **System Admin**: Đặc biệt highlight với màu đỏ

### 2. **Card Components**

#### Basic Card
```css
.card {
    border: none;
    border-radius: 8px;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.card:hover {
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
}
```

#### Stats Cards
- Large display numbers
- Icon indicators
- Action buttons
- Gradient backgrounds for admin features

### 3. **Form Components**

#### Enhanced Input Fields
```css
input, select, textarea {
    border-radius: 8px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    padding: 0.75rem 1rem;
    background: rgba(255, 255, 255, 0.9);
    -webkit-backdrop-filter: blur(5px);
    backdrop-filter: blur(5px);
}

input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(58, 134, 255, 0.1);
    background: rgba(255, 255, 255, 1);
}

/* Authentication form styling */
.auth-form {
    background: rgba(255, 255, 255, 0.95);
    -webkit-backdrop-filter: blur(15px);
    backdrop-filter: blur(15px);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: 2rem;
    position: relative;
    overflow: hidden;
}

.auth-form::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
}
```

#### Button System with Enhanced Effects
```css
.btn {
    border-radius: 50px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
    transition: var(--transition);
}

/* Primary Button with Gradient */
.btn-primary {
    background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
    border: none;
    color: var(--text-light);
}

/* Hover Effects with Shimmer */
.btn:after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.2);
    transform: skewX(-20deg);
    transition: all 0.6s ease;
}

.btn:hover:after {
    left: 100%;
}

/* Loading button state */
.btn-loading {
    pointer-events: none;
    opacity: 0.7;
}

.btn-loading::before {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    margin: auto;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

#### Advanced Form Validation
```css
/* Form validation states */
.form-control.is-valid {
    border-color: var(--success-color);
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 8 8'%3e%3cpath fill='%2338b000' d='m2.3 6.73.94-.94 1.84 1.84 3.15-3.15.94.94L4.25 8.25 2.3 6.73z'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right calc(0.375em + 0.1875rem) center;
    background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
}

.form-control.is-invalid {
    border-color: var(--danger-color);
    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23ff006e'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath d='m5.5 5.5 1 1 1-1M5.5 6.5l1-1 1 1'/%3e%3c/svg%3e");
    background-repeat: no-repeat;
    background-position: right calc(0.375em + 0.1875rem) center;
    background-size: calc(0.75em + 0.375rem) calc(0.75em + 0.375rem);
}

.valid-feedback {
    color: var(--success-color);
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.invalid-feedback {
    color: var(--danger-color);
    font-size: 0.875rem;
    margin-top: 0.25rem;
}
```

### 4. **Table Components**

#### Admin Tables
```css
.admin-table {
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.admin-table thead th {
    background-color: #3a4651;
    color: #ffffff;
    padding: 1rem;
    font-weight: 500;
    position: sticky;
    top: 0;
}
```

#### Status Badges
```css
.badge {
    padding: 0.5em 0.8em;
    font-weight: 500;
    border-radius: 30px;
}

.badge-success { background-color: #34ce57; }
.badge-warning { background-color: #f7b924; color: #212529; }
.badge-danger { background-color: #ff3e6c; }
.badge-info { background-color: #17a2b8; }
```

### 5. **Modal & Dialog Components**
- Backdrop blur effects
- Smooth animations
- Proper z-index layering
- Responsive sizing

---

## 📱 Responsive Design

### Breakpoints
```css
:root {
    --breakpoint-xs: 0;
    --breakpoint-sm: 576px;
    --breakpoint-md: 768px;
    --breakpoint-lg: 992px;
    --breakpoint-xl: 1200px;
}
```

### Mobile-First Approach
- Base styles cho mobile (< 576px)
- Progressive enhancement cho larger screens
- Flexible grid system
- Touch-friendly interface elements

### Responsive Patterns
```css
/* Stack cards on mobile */
@media (max-width: 767.98px) {
    .card { margin-bottom: 1rem; }
    .btn { font-size: 0.8rem; padding: 0.4rem 1.2rem; }
}

/* Optimize tables for mobile */
@media (max-width: 768px) {
    .table { display: block; overflow-x: auto; }
}
```

---

## 🎯 Role-Based UI Patterns

### 1. **Student Interface**
- Simplified navigation
- Focus on lab sessions và personal dashboard
- Educational color scheme
- Basic functionality access

### 2. **Admin Interface**
- Extended navigation với management tools
- Advanced table controls
- System monitoring components
- Bulk action capabilities

### 3. **System Administrator**
- Full system access
- Danger zone styling cho critical actions
- Advanced settings panels
- System health indicators

---

## 🎨 Animation & Interaction

### Transition System
```css
:root {
    --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* Smooth micro-interactions */
.card, .btn, input, .nav-link {
    transition: var(--transition);
}
```

### Enhanced Animation Library
```css
/* Shimmer effect for loading states */
@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Progress bar shimmer animation */
@keyframes progress-shimmer {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* Pulse animation for notifications */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(58, 134, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(58, 134, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(58, 134, 255, 0); }
}

/* Glow effect for interactive elements */
@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 5px rgba(58, 134, 255, 0.5); }
    50% { box-shadow: 0 0 20px rgba(58, 134, 255, 0.8); }
}

/* Page entrance animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}

/* Background animation for auth pages */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
```

### Interactive Elements
```css
/* Enhanced hover effects */
.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

/* Navbar link hover animations */
.navbar-dark .navbar-nav .nav-link:hover {
    color: var(--warning-color);
    transform: translateY(-2px);
}

/* Button shimmer effect */
.btn:after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.2);
    transform: skewX(-20deg);
    transition: all 0.6s ease;
}

.btn:hover:after {
    left: 100%;
}
```

---

## 📊 Data Visualization Components

### Progress Bars
```css
.progress {
    height: 8px;
    border-radius: 10px;
    background: #e9ecef;
    overflow: hidden;
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

.progress-bar {
    border-radius: 10px;
    transition: width 0.6s ease;
    position: relative;
    overflow: hidden;
}

.progress-bar::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    animation: progress-shimmer 2s infinite;
}
```

### Chart Containers
```css
.chart-container {
    position: relative;
    height: 300px;
    padding: 1rem;
    background: rgba(255, 255, 255, 0.95);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

.chart-container canvas {
    max-height: 100%;
    border-radius: var(--border-radius);
}
```

### Custom Scrollbars
```css
/* Enhanced scrollbar styling for data containers */
.system-metrics::-webkit-scrollbar {
    width: 8px;
}

.system-metrics::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 10px;
}

.system-metrics::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
    border-radius: 10px;
}

.system-metrics::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, var(--secondary-color), var(--primary-color));
}
```

---

## 🔄 Loading & State Management

### Loading Overlays
```css
#loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    -webkit-backdrop-filter: blur(5px);
    backdrop-filter: blur(5px);
    z-index: 9999;
    display: flex;
    justify-content: center;
    align-items: center;
}

#loading-overlay .spinner-border {
    width: 3rem;
    height: 3rem;
    border-width: 0.3em;
    color: var(--primary-color);
}
```

### Enhanced Flash Messages
```css
.flash-message {
    padding: 15px 20px;
    margin-bottom: 15px;
    border-radius: var(--border-radius);
    position: relative;
    overflow: hidden;
    box-shadow: var(--box-shadow);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
    animation: slideIn 0.5s ease forwards;
}

.flash-message:before {
    font-family: 'Font Awesome 5 Free';
    font-weight: 900;
    margin-right: 10px;
}

.flash-message.success {
    background-color: rgba(56, 176, 0, 0.1);
    color: var(--success-color);
    border-left: 4px solid var(--success-color);
}

.flash-message.success:before {
    content: '\f00c';
}

.flash-message.danger {
    background-color: rgba(255, 0, 110, 0.1);
    color: var(--danger-color);
    border-left: 4px solid var(--danger-color);
}

.flash-message.danger:before {
    content: '\f06a';
}

.flash-message.info {
    background-color: rgba(58, 134, 255, 0.1);
    color: var(--primary-color);
    border-left: 4px solid var(--primary-color);
}

.flash-message.info:before {
    content: '\f05a';
}
```

---

## 🌟 Advanced UI Patterns

### Glass Morphism Effects
```css
/* Glass effect for dashboard headers */
.dashboard-header {
    background: rgba(255, 255, 255, 0.1);
    -webkit-backdrop-filter: blur(15px);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: var(--border-radius);
    color: var(--text-light);
    box-shadow: var(--box-shadow);
}

/* Semi-transparent cards with blur */
.stat-card {
    background: rgba(255, 255, 255, 0.95);
    -webkit-backdrop-filter: blur(10px);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Enhanced Stat Cards
```css
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--card-accent-color, #007bff), var(--card-accent-color-light, #66b3ff));
}

.stat-card.primary::before {
    --card-accent-color: var(--primary-color);
    --card-accent-color-light: #66b3ff;
}

.stat-card.success::before {
    --card-accent-color: var(--success-color);
    --card-accent-color-light: #71dd8a;
}

.stat-card.info::before {
    --card-accent-color: var(--accent-color);
    --card-accent-color-light: #7cc7d0;
}

.stat-card.warning::before {
    --card-accent-color: var(--warning-color);
    --card-accent-color-light: #ffe066;
}
```

### Icon Animation Patterns
```css
.stat-icon {
    width: 70px;
    height: 70px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin: 0 auto 1.5rem auto;
    background: linear-gradient(135deg, var(--icon-bg-start), var(--icon-bg-end));
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
}

.stat-icon::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transform: rotate(45deg);
    animation: shimmer 1.5s ease-in-out;
}
```

---

## 📦 CSS Architecture

### File Organization
```
static/css/
├── base.css              # Core styles, variables, typography
├── log_regis.css         # Authentication pages
├── admin_tables.css      # Admin table components
├── system_dashboard.css  # Dashboard specific styles
├── responsive.css        # Responsive breakpoints
└── admin.css            # Admin-specific overrides
```

### CSS Custom Properties
```css
:root {
    /* Colors */
    --primary-color: #3a86ff;
    --secondary-color: #8338ec;
    
    /* Spacing */
    --border-radius: 8px;
    --box-shadow: 0 6px 14px rgba(0, 0, 0, 0.1);
    
    /* Transitions */
    --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
```

---

## 🎭 Theme Variations

### Light Theme (Default)
- Light backgrounds với subtle shadows
- Dark text trên light backgrounds
- Vibrant accent colors

### Dark Mode Support
```css
@media (prefers-color-scheme: dark) {
    body.auto-dark-mode {
        --text-color: #f8f9fa;
        --background-color: #212529;
        background-color: var(--background-color);
        color: var(--text-color);
    }
}
```

---

## 🔧 Implementation Guidelines

### 1. **Component Development**
- Follow BEM methodology cho CSS classes
- Use CSS custom properties cho theming
- Implement progressive enhancement
- Test across different devices và browsers

### 2. **Performance Optimization**
- Minimize CSS bundle size
- Use CSS transforms cho animations
- Implement critical CSS loading
- Optimize for Core Web Vitals

### 3. **Maintenance**
- Document any design system changes
- Keep component library updated
- Regular accessibility audits
- Browser compatibility testing

---

## 📋 Component Checklist

### ✅ Implemented Components
- [x] Navigation (Navbar, Dropdowns, Enhanced hover effects)
- [x] Cards (Basic, Stats, Admin with glass morphism)
- [x] Forms (Enhanced inputs, Advanced validation, Loading states)
- [x] Tables (Admin tables, Responsive, Custom scrollbars)
- [x] Modals và Dialogs (Backdrop blur, Smooth animations)
- [x] Authentication UI (Glass effects, Animated backgrounds)
- [x] Dashboard Components (System metrics, Progress bars)
- [x] Status Badges và Indicators (Enhanced with icons)
- [x] Loading States (Overlays, Spinners, Shimmer effects)
- [x] Flash Messages (Animated, Icon-enhanced, Backdrop blur)
- [x] Animation Library (Comprehensive keyframes and transitions)
- [x] Data Visualization (Progress bars, Chart containers)

### 🚧 Future Enhancements
- [ ] Advanced chart components (D3.js integration)
- [ ] Real-time notification system with WebSocket
- [ ] Progressive Web App features (Service workers, Offline support)
- [ ] Advanced theming options (Multiple color schemes)
- [ ] Accessibility enhancements (Voice navigation, High contrast mode)
- [ ] Mobile-specific gestures and interactions
- [ ] Print-friendly styles for reports

---

## 📖 Usage Examples

### Creating a New Admin Page
```html
{% extends "index.html" %}
{% block styles %}
{{ super() }}
<link rel="stylesheet" href="{{ url_for('static', filename='css/admin_tables.css') }}">
{% endblock %}

{% block content %}
<div class="container">
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h3><i class="fas fa-cog"></i> Page Title</h3>
        </div>
        <div class="card-body">
            <!-- Content here -->
        </div>
    </div>
</div>
{% endblock %}
```

### Adding a New Button Style
```css
.btn-custom {
    background: linear-gradient(45deg, #custom-color-1, #custom-color-2);
    border: none;
    /* Follow existing button patterns */
}
```

### Implementing New Dashboard Cards
```html
<div class="col-md-4">
    <div class="stat-card success" data-animation="fadeIn">
        <div class="stat-icon">
            <i class="fas fa-users"></i>
        </div>
        <h3 class="stat-number">{{ user_count }}</h3>
        <p class="stat-label">Active Users</p>
        <div class="progress">
            <div class="progress-bar bg-success" style="width: 85%"></div>
        </div>
    </div>
</div>
```

### Creating Animated Flash Messages
```python
# Flask route example
flash('Operation completed successfully!', 'success')
flash('Warning: Please review your input.', 'warning')
flash('Error: Unable to process request.', 'danger')
```

### Adding Loading States
```javascript
// JavaScript example for loading states
function showLoading(button) {
    button.classList.add('btn-loading');
    button.disabled = true;
}

function hideLoading(button) {
    button.classList.remove('btn-loading');
    button.disabled = false;
}
```

---

**Lab Manager Design System v1.2**  
*Tài liệu này mô tả hệ thống thiết kế hoàn chỉnh cho ứng dụng Lab Manager, bao gồm tất cả các component, pattern và guideline cần thiết để đảm bảo tính nhất quán và khả năng mở rộng cho tương lai.*

**Last Updated:** January 2025  
**Maintainer:** Lab Manager Development Team

## 📝 Version History

- **v1.0** - Initial design system documentation
- **v1.1** - Added responsive patterns and role-based UI
- **v1.2** - Enhanced with animation library, data visualization components, and advanced UI patterns

---

---

## 🏗️ Layout & Grid Systems

### Background Patterns
```css
/* Code-inspired grid pattern for authentication pages */
body:before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255, 255, 255, 0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.07) 1px, transparent 1px);
    background-size: 20px 20px;
    z-index: -1;
}

/* Animated gradient backgrounds */
.gradient-bg {
    background: linear-gradient(-45deg, var(--primary-color), var(--secondary-color), var(--accent-color), var(--primary-color));
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}
```

### Container Systems
```css
.auth-container {
    width: 100%;
    max-width: 800px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.system-dashboard {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    min-height: 100vh;
    padding: 0;
}
```

### Flash Message System
```css
.flash-messages {
    width: 100%;
    margin-bottom: 20px;
    max-width: 800px;
    position: relative;
    z-index: 9999; /* Ensure flash messages are always on top */
}
```