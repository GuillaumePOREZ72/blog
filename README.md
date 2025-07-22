# Blog Project

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=ffffff)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=000000)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=ffffff)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwind-css&logoColor=ffffff)

## Project Description

The Blog Project is a full-stack web application that allows users to create, read, and write blog posts. This application is designed to provide a seamless experience for both blog readers and contributors, featuring a clean and responsive user interface built with React and styled using Tailwind CSS. The backend is powered by Python, utilizing a structured approach to manage blog data and handle routing.

### Key Features
- User-friendly interface for reading and writing blog posts
- Responsive design for optimal viewing on various devices
- Modular architecture for easy maintenance and scalability

## Tech Stack

| Technology       | Description                          |
|------------------|--------------------------------------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=ffffff) | Backend language used for server-side logic |
| ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=000000) | Frontend library for building user interfaces |
| ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=ffffff) | Build tool that serves the frontend application |
| ![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwind-css&logoColor=ffffff) | CSS framework for styling the application |

## Installation Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js (for frontend)
- npm or pnpm (for package management)

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/GuillaumePOREZ72/blog.git
   cd blog
   ```

2. **Set up the backend**
   - Navigate to the backend directory:
   ```bash
   cd backend
   ```
   - Create a virtual environment:
   ```bash
   python -m venv venv
   ```
   - Activate the virtual environment:
     - On Windows:
     ```bash
     venv\Scripts\activate
     ```
     - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Install required packages (if a requirements.txt file exists, otherwise install manually):
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   - Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
   - Install the dependencies:
   ```bash
   npm install
   ```
   or if using pnpm:
   ```bash
   pnpm install
   ```

4. **Environment Variables**
   - If there are any environment variables required, create a `.env` file in the `backend/app` directory and configure it according to your setup.

## Usage

### Running the Project
1. **Start the backend server**
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend application**
   ```bash
   cd frontend
   npm run dev
   ```
   or if using pnpm:
   ```bash
   pnpm run dev
   ```

### Basic Usage
- Access the application in your web browser at `http://localhost:3000` (or the port specified by your Vite configuration).

## Project Structure

```
blog/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── post.py           # Model for blog posts
│   │   ├── routes/
│   │   │   └── post_routes.py     # Routes for handling blog post requests
│   │   ├── config.py              # Configuration settings for the backend
│   │   └── main.py                # Entry point for the backend application
│   └── venv/                      # Virtual environment for Python dependencies
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── BlogCard.jsx       # Component for displaying a blog card
    │   │   └── Loading.jsx         # Loading component for async operations
    │   ├── pages/
    │   │   ├── BlogDetail.jsx      # Page for displaying a single blog post
    │   │   ├── BlogList.jsx        # Page for listing all blog posts
    │   │   └── WriteBlog.jsx       # Page for writing new blog posts
    │   ├── App.jsx                 # Main application component
    │   └── main.jsx                # Entry point for the frontend application
```

## Contributing

Contributions are welcome! Please follow these guidelines:
- Fork the repository and create a new branch for your feature or bug fix.
- Ensure your code adheres to the project's coding standards.
- Submit a pull request with a clear description of your changes. 

Thank you for your interest in contributing to the Blog Project!
