# RAT (Remote Access Tool)

A lightweight remote management and command-and-control (C2) framework project built with Python and supported by Gradle.

---

## 📁 Project Structure

```text
RAT/
├── .gradle/                  # Gradle internal caches
├── gradle/
│   └── wrapper/             # Gradle wrapper files
├── output/                   # Directory for generated builds and logs
├── c2.py                     # Command & Control server script
├── main.py                   # Main client / agent application script
├── gradlew / gradlew.bat     # Gradle wrapper executable scripts
├── settings.gradle           # Gradle settings configuration
└── README.md                 # Project documentation
```

---

## 🚀 Prerequisites

Ensure you have the following installed on your target system:

* **Python**: `3.8+`
* **Java Development Kit (JDK)**: `21` (or compatible version)
* **Gradle**: Handled automatically via `./gradlew`

---

## 🛠️ Usage & Setup

### 1. Initialize the Environment

Ensure executable permissions for the Gradle Wrapper (Linux/macOS):

```bash
chmod +x gradlew
```

Verify your Gradle Wrapper configuration:

```bash
./gradlew wrapper
```

### 2. Build the C2 Server

Start the Command to build the RAT for targets:

```bash
python c2.py
```

### 3. Build a Controller script

Execute the script in the terminal:

```bash
python main.py
```

---

## ⚠️ Disclaimer

> **Important**: This software is provided for educational and authorized testing purposes only. Usage of this tool against targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state, and federal laws.
