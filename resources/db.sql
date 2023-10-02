/**
 ** Database schema
 ** ---------------
 ** This file contains the database schema for the project
 **/

-- Create table users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    user_role VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    created_at DATETIME,
    updated_at DATETIME
);

-- create table projects
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    description TEXT,
    storageSchema TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- make an fk many to many table relation between users and projects
CREATE TABLE users_projects (
    user_id INTEGER,
    project_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    created_at DATETIME,
    updated_at DATETIME,
);

-- create table registrees
-- image, optimizedimage, fk(project_id)
CREATE TABLE registrees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image TEXT,
    optimized_image TEXT,
    project_id INTEGER,
    FOREIGN KEY(project_id) REFERENCES projects(id),
    created_at DATETIME,
    updated_at DATETIME
);

-- create table registree_details
-- fk(registree_id), kv_key, kv_value, kv_type
CREATE TABLE registree_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registree_id INTEGER,
    kv_key VARCHAR(255),
    kv_value TEXT,
    kv_type VARCHAR(255),
    FOREIGN KEY(registree_id) REFERENCES registrees(id),
    created_at DATETIME,
    updated_at DATETIME
);

-- create database triggers for all update and created at fields
CREATE TRIGGER users_created_at AFTER INSERT ON users
BEGIN
    UPDATE users SET created_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER users_updated_at AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER projects_created_at AFTER INSERT ON projects
BEGIN
    UPDATE projects SET created_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER projects_updated_at AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER users_projects_created_at AFTER INSERT ON users_projects
BEGIN
    UPDATE users_projects SET created_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER users_projects_updated_at AFTER UPDATE ON users_projects
BEGIN
    UPDATE users_projects SET updated_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER registrees_created_at AFTER INSERT ON registrees
BEGIN
    UPDATE registrees SET created_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER registrees_updated_at AFTER UPDATE ON registrees
BEGIN
    UPDATE registrees SET updated_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER registree_details_created_at AFTER INSERT ON registree_details
BEGIN
    UPDATE registree_details SET created_at = DATETIME('NOW') WHERE id = new.id;
END;

CREATE TRIGGER registree_details_updated_at AFTER UPDATE ON registree_details
BEGIN
    UPDATE registree_details SET updated_at = DATETIME('NOW') WHERE id = new.id;
END;