# Bike Finder
#### Video Demo: https://youtu.be/FaTC-bAddC8
#### Description:

## Introduction

Bike Finder is a web application designed to help individuals discover their ideal motorcycle or scooter without requiring in-depth knowledge of bikes. Motorcycles can be intimidating for beginners, especially when faced with technical specifications like engine capacity, torque, or mileage. This project bridges that gap by offering a user-friendly interface that recommends bikes and scooters, provides a searchable database, and allows users to save favorites to a personal wishlist.

The application leverages the Flask framework for backend development, SQLite for database management, and HTML, CSS, and JavaScript for the frontend. Additionally, Jinja templating is used to dynamically render content on the website. The end result is an intuitive platform that makes bike selection accessible to all users, regardless of prior expertise.

---

## Motivation

The idea for Bike Finder came from the challenge many people face when trying to choose their first motorcycle or scooter. With a vast number of models on the market, it is easy for beginners to feel overwhelmed by technical jargon. I wanted to create a tool that simplifies this decision-making process by curating recommendations and enabling keyword-based searches.

Another motivation was to gain practical experience in building a full-stack application by combining knowledge from CS50: backend logic, frontend design, databases, and APIs.

---

## Project Overview

From the user’s perspective, Bike Finder offers the following functionality:

1. **Bike and Scooter Recommendations** – Users can browse curated lists of recommended bikes and scooters.
2. **Search Feature** – A fully functional search bar allows users to query the database for specific models.
3. **User Authentication** – Registration and login ensure that each user can securely access their account.
4. **Wishlist** – Logged-in users can save bikes they are interested in to a personal wishlist.
5. **Media Content** – The website includes an introductory video and images to enhance the browsing experience.

Through these features, Bike Finder aims to serve both casual visitors and registered users who wish to track and organize their preferences.

---

## File Breakdown

* **app.py**: The main Flask application that handles routing, user authentication, and core logic.
* **config.py**: Stores configuration variables for the application, including session settings and database connections.
* **helpers.py**: Contains utility functions, such as decorators for login requirements or helper methods for handling queries.
* **users.db**: SQLite database storing user information, login credentials, and wishlist data.
* **/static/**: Holds all static files including images, JavaScript, CSS, and videos.

  * `images/`: Contains images like the project logo and placeholders for upcoming content.
  * `js/`: Includes `search.js` and `wishlist.js` which handle client-side interactivity such as searching and managing the wishlist dynamically.
  * `videos/`: Contains a short bike video to make the site engaging.
  * `styles.css`: Provides styling for the overall look and feel of the site.
* **/templates/**: Contains all HTML files rendered via Jinja.

  * `layout.html`: The base template inherited by all other pages.
  * `index.html`: Homepage introducing the site.
  * `login.html`, `register.html`: Authentication pages.
  * `wishlist.html`: Displays the logged-in user’s wishlist.
  * `search_results.html` and `result.html`: Display search outcomes and detailed results.
  * `news.html`: Placeholder or optional feature for bike-related updates.
  * `error.html`: Handles user-facing error messages.
* **README.md**: This documentation file.

---

## Design Choices

The decision to use **Flask** was made due to its lightweight structure and flexibility, making it ideal for a project of this size. Jinja templating simplified the dynamic rendering of content across multiple pages.

For storing user data, **SQLite** was selected as it integrates well with Flask, is lightweight, and sufficient for this project’s scale.

On the frontend, I opted for a clean separation of concerns: CSS for styling, JavaScript for interactivity, and HTML for structure. Organizing static files into dedicated folders (images, videos, js) ensures scalability and maintainability.

One debated choice was whether to use an API for real-time bike data or rely on a pre-loaded database. Due to the complexity and time constraints of implementing APIs reliably, I opted to begin with a local database while leaving the possibility of API integration for future development.

---

## Challenges Faced

One of the most significant challenges was implementing an API for retrieving real-time data about motorcycles. While I experimented with APIs, integration proved challenging due to inconsistent data availability and authentication requirements. As a result, I decided to focus on strengthening the local database first.

Another challenge was managing user sessions securely. Flask’s session handling and CS50’s guidance on login decorators helped ensure user-specific data was isolated and secure.

Additionally, ensuring smooth interactivity with JavaScript for features like the search bar and wishlist required careful debugging to synchronize backend responses with frontend actions.

---

## Testing

Testing was carried out in multiple phases:

* **Unit Testing**: Core functions in `helpers.py` were tested with sample inputs to ensure correct outputs.
* **Manual Testing**: Various user scenarios such as registering, logging in, adding to wishlist, and searching were performed to confirm expected behavior.
* **Error Handling**: Incorrect login attempts, invalid search queries, and edge cases (like an empty wishlist) were tested to ensure the system responds gracefully.
* **Valgrind / Flask Debugger**: Used to confirm memory and session handling were efficient.

---

## Limitations and Future Work

While functional, Bike Finder currently has limitations:

* The database is static and does not pull live data from manufacturers.
* The recommendation system is based on preset logic rather than advanced filtering or AI-driven personalization.
* The UI can be further polished with more responsive design for mobile devices.

In future versions, I plan to:


* Improve search by adding filters (price, mileage, brand).
* Expand the recommendation system to be more intelligent.
* Add social features, such as sharing wishlists with friends.

---

## Conclusion

Bike Finder has been a rewarding project that brought together skills across multiple domains: web development, database management, user authentication, and client-side interactivity. Through this process, I not only reinforced my understanding of Flask and SQL but also learned how to structure a full-stack application in a way that is scalable and maintainable.

Although there are areas for improvement, I am proud of the progress made and the functionality delivered within the scope of CS50. This project represents my growth as a programmer and my ability to take an idea from concept to execution.

---




