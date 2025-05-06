# WISHLISTS
# name: Zach McNulty
# Github: zachlearnscode
# edX: zmcnulty980
# city: Independence
# state: Missouri
# country: USA
#### Video Demo (recorded 5/6/2025):  <URL HERE>
#### Description: Wishlists is a collaborative CRUD application that enables users to plan their gift-giving for upcoming birthdays or other celebrations. 

#### Say your mother's birthday is next month. As a Wishlists user, you create a new wishlist for the event and invite others to join. Together, you can post your birthday gift ideas for mom. From inside the wishlist, users can claim certain gifts, and mark them as acquired so everyone knows who's getting what for mom. It's a lot like a registry, but it's completely agnostic to any retailer.

#### I took the CS50 final project as a challenge to build and deploy a full stack web application. I have several years of frontend development experience and wanted to push myself outside of my comfort zone with the skills I learned in CS50: particularly server-side code and SQL. Along the way, I found unique challenges in implementing user authentication tools provided by Google Firebase as well as deploying the apps to external servers.

#### Wishlists is built with the following tech stack:
* Front-end
  * Vite
  * Vue3 (and several supporting libraries)
  * TailwindCSS
  * DaisyUI
  * HeadlessUI
* Back-end
  * FastAPI (Python)
  * SQLModel (SQLAlchemy and Pydantic)
  * SQLite
* Other
  * Firebase Authentication
  * Firebase Cloud Functions
* Hosting
  * Frontend: Firebase
  * Backend: Digital Ocean

#### What to Know
#### On the front end, there are several important files. Among them are:
* firebase.js: establishes a connection to my firebase project, where user auth and a single cloud function are managed
* .env.* files: enables app to seamlessly switch between environments with the exact same codebase
* src/stores/auth: enables app to monitor the user's authorization status from firebase
* src/router: Enforces auth requirements as users try different routes in the app
*src/functions/index: Define a firebase cloud function that makes a call to the backend to create a user record in my SQLite database to be used for purposes beyond authentication
* src/api: modifies every api request to include the firebase user's Bearer token, allowing the backend to validate each user is authorized before responding to requests
* main.js; index.html; src/App: a combination of files that comprise the UI when the project is built

#### On the back end:
* main.py: Because I'm less familiar with backend development (and Python in general), I crammed most all of my backend source code into this single file. Going forward, this is one area that's ripe for improvement. Toward the top of the file, you'll see each of my database tables defined with SQLModel. These include User, Wishlist, WishlistUserLink and Item. I recruited help from ChatGPT to build the database schema and table definitions and tweaked them along the way to suit my needs. I was extremely pleased with ChatGPT, which suggested fields such as: items: List["Item"] = Relationship(back_populates="wishlist") in the Wishlist table. It might have taken me months experimenting with SQLModel/SQLAlchemy to even notice this feature, which makes defining and returning robust response_models extremely efficient. When the script is run, is locates/creates a SQLite DB file, connects to it and creates the tables. The file also establishes a connection to firebase_admin, which allows me to validate that the Bearer token in each request is tied to a currently authenticated user before proceeding with any endpoint logic. Finally, the FastAPI app is initialized and the rest of the file is comprised of endpoint definitions. As a whole, this file comprises an API that allows authorized users to make requests to modify the database, which ultimately defines their experience with the app.

#### Hosting
* frontend: The front end Vue application is hosted on Firebase. This is also where my user authentication and cloud function live. This was simple to set up with the firebase CLI, which generated a configuration file on my behalf and simply requires running the command firebase deploy to make changes on the server.
* backend: You can probably tell I don't know much about devops by my decision to host the backend on a totally different server. This turned out to be an educational experience though, as it was much more hands on than firebase hosting. Again, I leaned on ChatGPT to help navigate this process. My backend is running python and nginx on linux ubuntu. Throughout this project, I learned that AI can be extremely helpful in improving development speed and efficiency, but it's not replacement for a user's own skill, experience and knowledge. ChatGPT was able to get me about 80% of the way to successfully deploying my server code before my requests started returning failure to connect errors. As someone almost completely unfamiliar with linux servers and tools like nginx, I didn't get much help from ChatGPT from that simple error report. To get thing's up and running finally, I had to do a lot of research and trial and error to find the root cause of the issue (SSL certificating and nginx server config) before I was able to get it rectified.

#### Next steps:
Immediate next steps are to reestablish a reliable local development environment. I'd like to seed my staging database with some more robust data. I'd like to add more features, like the ability to combine wishlists or comment on items or plan more than just items. It would be awesome if I could convert this into a mobile app as well. But for now, I'm so pleased to have deployed a full stack application and (hopefully) completed CS50. Thank you!