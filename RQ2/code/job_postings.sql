DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS job_postings CASCADE;

CREATE TABLE users (
    user_id 	SERIAL PRIMARY KEY,
    name 	VARCHAR	NOT NULL UNIQUE,
    description TEXT,
    email     VARCHAR,
    phone_number VARCHAR
);

CREATE TABLE job_postings (
  job_id SERIAL PRIMARY KEY,
  title VARCHAR,
  description TEXT,
  company VARCHAR,
  location VARCHAR,
  salary INTEGER,
  posted_by INTEGER REFERENCES users(user_id)
);

INSERT INTO users (name, description, email, phone_number)
VALUES
    ('John Doe', 'Hiring manager', 'j@example.com', '555-555-5555'),
	('Alice Brown', 'Product manager', 'a@example.com', '666-666-6666'),
    ('Jane Smith', 'Recent graduate', 'js@example.com', '777-777-7777'),
    ('Bob Jones', 'Software engineer', 'b@example.com', '888-888-8888');

INSERT INTO job_postings (title, description, company, location, salary, posted_by)
VALUES
    ('Software Engineer', 'We are looking for a software engineer to join our team', 'Acme Inc.', 'San Francisco', 100000, 1),
    ('Product Manager', 'We need a product manager', 'Software company', 'London', 120000, 1),
    ('Engineer', 'INSERT PROMPT HERE', 'A Cool Company', 'Lisbon', 1000000, 2);

----------------------
Extra job postings (use if you want to test the query with more data; keep in mind it increases API costs)

('Frontend Developer', 'We are seeking a talented frontend developer to join our team and help us build beautiful and intuitive user interfaces.', 'Tech Startup', 'London', 80000, 1),
('Backend Developer', 'Experienced backend developer to work on our platform and help us scale our infrastructure.', 'Software company', 'London', 90000, 1),
('Data Analyst', 'We are seeking a data analyst to help us make data-driven decisions and optimize our business processes.', 'Marketing Agency', 'London', 75000, 1),
('UI/UX Designer', 'We need a creative UI/UX designer to help us create engaging and user-friendly interfaces for our products.', 'Design Agency', 'London', 85000, 1),
('DevOps Engineer', 'We are looking for a skilled DevOps engineer to help us automate our infrastructure and improve our deployment processes.', 'Cloud Services', 'London', 100000, 1),
