# Mehndi Booking Service

A Django web application for booking mehndi (henna) designs for various occasions.

## Features

### User Module
- User registration and authentication
- Browse gallery of mehndi designs
- Filter designs by category
- Book designs or create custom bookings
- View booking history and status
- Submit feedback and ratings
- Payment management

### Admin Module
- Admin dashboard with statistics
- Manage categories, subcategories, and designs
- View and manage all customer bookings
- Process payments
- Handle customer feedback
- View list of all registered customers

## User Roles

### Customer
When a customer logs in, they are redirected to their user dashboard which includes:
- Personal booking statistics
- Quick access to gallery and booking features
- Custom booking creation
- Booking management
- Feedback submission

### Admin
When an admin logs in, they are redirected to the admin dashboard which includes:
- Business statistics (total bookings, pending bookings, designs, feedback)
- Content management (categories, subcategories, designs)
- Business management (bookings, payments, feedback)
- Customer management

## Navigation

### Admin Navigation Menu
- Dashboard
- Content Management
  - Categories
  - Sub-categories
  - Designs
- Business Management
  - Bookings
  - Payments
  - Feedback
  - Customers

### User Navigation Menu
- Dashboard
- Gallery
- My Bookings
- Custom Booking
- Feedback

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

## Default Admin Credentials
- Username: admin
- Password: admin

## Project Structure
- `accounts/` - User authentication and profiles
- `gallery/` - Design gallery management
- `booking/` - Booking system
- `admin_panel/` - Admin interface and management
- `mehndi_booking/` - Main project settings and configuration

## Models
- User (Custom user model with customer/admin roles)
- Category
- SubCategory
- Design
- Booking
- Payment
- Feedback