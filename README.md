# Secure Health Record System (SRHS)

A modern, secure, and user-friendly web application for managing, sharing, and analyzing medical records. Built with Flask, this system empowers patients and doctors with robust access control, advanced analytics, and an integrated AI assistant.

---

## Features

- **End-to-End Security:** All medical data is encrypted and access-controlled.
- **Role-Based Dashboards:** Separate, intuitive dashboards for patients and doctors.
- **Controlled Access:** Patients can grant or revoke access to their records for healthcare providers.
- **Easy Uploads:** Upload and manage medical reports (PDFs, images) with a simple interface.
- **AI Assistant:** Integrated chatbot for intelligent search and health insights.
- **Smart Analytics:** Visualize and analyze health data with built-in tools.
- **Mobile Friendly:** Responsive design for seamless use on any device.
- **Audit Trails:** Track access and changes to sensitive data.
- **Extensible:** Modular codebase for easy feature expansion.

---

## Demo

![Demo Screenshot](static/img/medical_illustration.svg)

---

## Getting Started

### 1. **Clone the Repository**

```bash
git clone https://github.com/maybemnv/SRHS.git
cd SRHS
```

### 2. **Set Up a Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Set Environment Variables**

Create a `.env` file (or set these in your environment):

```
FLASK_APP=main.py
FLASK_ENV=production
SESSION_SECRET=your-very-secure-secret
```

### 5. **Initialize the Database**

The database will be created automatically on first run. If you want to manually initialize or reset:

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

### 6. **Run the Application (Development)**

```bash
python main.py
# or
flask run
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

---

## Deployment

### **Production (Gunicorn + Reverse Proxy)**

1. **Install Gunicorn:**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 main:app
   ```

3. **(Recommended) Use a Reverse Proxy (e.g., Nginx):**
   - Forward requests from port 80/443 to Gunicorn.
   - Serve static files directly via Nginx for better performance.

4. **Environment Variables:**
   - Set `SESSION_SECRET` and other sensitive configs securely in your environment.

5. **Database:**
   - For production, consider using PostgreSQL (update `SQLALCHEMY_DATABASE_URI`).

---

## Folder Structure

```
SRHS/
  app.py
  main.py
  models.py
  routes.py
  forms.py
  requirements.txt
  static/
  templates/
  health_records.db
```

- The `secure-medical-report-system/` folder contains a more modular, extensible, and feature-rich version, including an AI chatbot and improved security.

---

## AI Chatbot

- The system includes an AI-powered chatbot to assist users with health queries, report navigation, and analytics.
- Built using state-of-the-art NLP libraries (`transformers`, `spaCy`, `nltk`, etc.).
- Can be extended for custom medical Q&A or integration with external APIs.

---

## Testing

```bash
pytest
```

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)

---

## Authors

- Manav Kaushal (maybemnv@gmail.com)

---

**For questions or support, please open an issue or contact the maintainer.**
