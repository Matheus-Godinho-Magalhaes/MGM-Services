# MGM Services - Service Marketplace
#### Video Demo: https://youtu.be/pCvmzOasFEA
#### Description:

MGM Services is an online marketplace designed to connect clients with service providers through a streamlined and accessible platform. This project, created as the final project for Harvard’s CS50x course, allows users to register as either a Client or a Provider. Clients can browse, filter, and book services based on their preferences, while Providers can manage their service listings and upcoming appointments.

The goal of MGM Services is to make service access more streamlined for both parties, enhancing the user experience with a robust search function, reliable scheduling, and a clear rating system that aids clients in choosing trusted providers.

This README provides a thorough overview of the project's functionality, design choices, and detailed descriptions of each key file.

### Project Overview

The core objective of MGM Services is to simplify the process of connecting clients with a wide range of service providers, allowing both parties to benefit from a user-friendly scheduling and rating system. The platform includes a secure login and registration system, with customized interfaces and permissions for Clients and Providers, which enhance user engagement and efficiency. Additionally, the platform enables service Providers to manage their profiles and bookings through a dedicated dashboard.

### Key Features

1. **Role-Based Accounts**:
   - **Clients** can browse Providers, filter services by type and location, and schedule appointments.
   - **Providers** have a personal dashboard where they can view upcoming appointments, edit profile information, and respond to booking requests.

2. **Scheduling and Rating System**:
   - Clients can easily schedule services with Providers, and after completion, they can leave ratings and comments, helping future clients make informed choices.

3. **Responsive Design**:
   - The front end, built with Bootstrap, ensures compatibility across devices, enhancing the user experience on mobile, tablet, and desktop screens.

4. **Security**:
   - Implements user authentication, session management, and role-based access control to protect sensitive information.

### Project Files and Structure

Below is a breakdown of each file in the project, along with its role in the overall application:

- **app.py**: This is the main application file, containing the Flask server configuration and route handling. It defines each route, from authentication to booking, and links to functions in `helpers.py` for data processing and validation.

- **helpers.py**: Contains helper functions used throughout the app, including `apology()` for custom error messages, along with functions for managing user sessions and database queries.

- **dados.db**: The SQLite database, storing essential data for the app. Tables include:
  - **users**: Stores user information (name, role, email, hashed password).
  - **appointments**: Stores booking data, linking clients with providers, and containing details such as appointment date and status.
  - **ratings**: Stores client reviews and ratings of providers, used to display feedback on provider profiles.
  - **services**: Stores providers serviceinformation (service type, price, location)

#### HTML Templates

1. **layout.html**: The base template that includes the navigation bar and footer. All pages extend this template for a consistent layout.

2. **index.html**: The home page, displaying a list of service providers with filters for service type and location, allowing clients to find and book Providers.

3. **home.html**: Provides a brief introduction to MGM Services, explaining its purpose and features to first-time visitors.

4. **login.html**: The login page where registered users can authenticate to access the platform.

5. **register.html**: The registration form where users can create accounts, choosing between Client and Provider roles.

6. **profile.html**: Allows users to view and manage their profile details. Clients can update personal information, while Providers have additional options for profile editing.

7. **provider_dashboard.html**: A dedicated dashboard for Providers, displaying upcoming appointments and profile management options.

8. **view_profile.html**: Displays a provider’s public profile with ratings and comments from previous clients.

9. **rate_provider.html**: A form that allows clients to leave a rating and comment on a provider after an appointment.

10. **history.html**: Displays the user’s appointment history. For Providers, it shows ratings and feedback received; for Clients, it shows ratings and feedback given.

11. **apology.html**: This template is used to display error messages when issues arise (e.g., failed login or booking error).

### Design and Development Choices

- **Bootstrap Framework**: Chosen for its responsive design capabilities and fast development time, Bootstrap provides a user-friendly experience across all devices.

- **Database Design**: Each user’s role, appointments, and ratings are organized into separate tables in `dados.db`. This structure helps efficiently manage data, with each user’s activities linked to their unique user ID.

- **Error Handling**: The `apology.html` page is used to display user-friendly error messages, improving the user experience by explaining issues clearly.

- **Security Measures**: This project implements best practices for protecting user data, including session management, password hashing, and route-based access control.

### Future Enhancements

Possible future updates include:
- Extending profile options for Providers to include more detailed service descriptions and image uploads.
- Adding a real-time notification system to update Providers when they receive a new booking or client message.
- Enhancing the scheduling system with options for managing cancellations and rescheduling.
- Enhanced Notification System: Adding email or SMS notifications for appointments.
- Expanded Search and Filter: Including more filter options for more precise searches.
- Payment Integration: Allowing clients to pay for services directly through the platform.

This project aims to showcase a full-featured service marketplace platform, utilizing skills and concepts from CS50x, from Flask and SQLite to front-end design with HTML, CSS, and Bootstrap.
