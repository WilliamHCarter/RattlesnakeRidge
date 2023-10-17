# Rattlesnake Ridge

> Multi-agent ML mystery game, powered by LangChain

<p>
  <img alt="Python" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white" height="25"/>
  <img alt="LangChain" src="https://img.shields.io/badge/-LangChain-2C4F7C?style=flat-square" height="25"/>
</p>

## Overview

In Rattlesnake Ridge, the player faces off against 4 AI Agents (Powered by the OpenAI API) in order to solve a mystery in a small western town. These AI agents are aware of some facts surrounding the case, and may provide clues to the player, or deceive the player, based on the scenario and their role in the crime that the player is investigating.

## Quick Start

To get started with this project, follow these steps:

### 1. Clone the repository:

   ```bash
   git clone https://github.com/WilliamHCarter/RattlesnakeRidge.git
   cd RattlesnakeRidge
   ```

### 2. Install dependencies:

  **Python**
   
   Make sure you have Python installed. If not, you can download and install Python from [python.org](https://www.python.org/downloads/).

   It's recommended to use a virtual environment to keep your project dependencies isolated:

   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate the virtual environment
   # For Windows:
   venv\Scripts\activate

   # For MacOS and Linux:
   source venv/bin/activate
   ```

   **Docker**
   
   This project is containerized using Docker. Make sure you have Docker installed. If not, you can download and install Docker from [Docker's official website.](https://www.docker.com/)

   **Node & NPM**
   
   This project uses NPM for its frontend dependency installation. Make sure you have node installed. If not, you can download and install Node.js from [nodejs.org](https://nodejs.org/). npm is included with the Node.js installation.

### 3. Add API Key:

   Create a file named `.env`, and paste the contents of `.env.template` into it.
   Then, add your key to the `LLM_API_KEY` variable inside your new `.env` file.

### 4. Run Flask App:

   Build the Docker image and run it as a container:

   ```bash
   # Build the Docker image
   docker build -t my-server .

   # Run the Docker container
   docker run -p 5000:5000 --env-file=.env my-server

   ```

   The Flask app will be accessible at [http://localhost:5000](http://localhost:5000/).

### 5. Run Frontend

   Navigate to the `client` directory and run the commands:
   ```
   npm install
   npm run dev
   ```
   This will open up a new UI instance at [http://localhost:5173](http://localhost:5173/) which you can use to interact with the app.
