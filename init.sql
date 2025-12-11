CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  description VARCHAR(255) NOT NULL,
  duedate DATE,
  completed BOOLEAN DEFAULT FALSE
);