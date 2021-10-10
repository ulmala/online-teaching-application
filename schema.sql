CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    role INT
);

CREATE TABLE IF NOT EXISTS courses(
    id SERIAL PRIMARY KEY,
    teacher_id INTEGER REFERENCES users,
    name TEXT,
    description TEXT,
    visible BOOLEAN
);

CREATE TABLE IF NOT EXISTS course_students(
    course_id INT REFERENCES courses,
    student_id INT REFERENCES users,
    UNIQUE (course_id, student_id)
);

CREATE TABLE IF NOT EXISTS tasks(
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses,
    question TEXT,
    visible BOOLEAN
);

CREATE TABLE IF NOT EXISTS answers(
    id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks,
    answer TEXT,
    correct BOOLEAN
);

CREATE TABLE IF NOT EXISTS results(
    id SERIAL PRIMARY KEY,
    task_id INT REFERENCES tasks,
    user_id INT REFERENCES users,
    result INT,
    UNIQUE (task_id, user_id)
);

CREATE TABLE IF NOT EXISTS materials(
    id SERIAL PRIMARY KEY,
    course_id INT REFERENCES courses,
    name TEXT,
    data bytea
);