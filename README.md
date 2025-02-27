## Prerequisites

- Python 3.8+
- Node.js 16+
- npm 8+ or yarn
- Virtual environment (venv)

### Clone the repository

- git clone https://github.com/uttkarsh-8/Steganographic-tool.git

- Navigate into the folder

## Backend Setup

### Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate

### Install the required Python packages:

pip install fastapi uvicorn pillow python-multipart cryptography

## Frontend Setup

Navigate to the React frontend directory:

- cd react-frontend/stego-frontend

Install the required npm packages:

- npm install

Start the Backend

- uvicorn app:app --reload

Start the Frontend

- cd react-frontend/stego-frontend
- npm run dev
- The frontend will be available at http://localhost:5173
