from typing import List
from datetime import datetime
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent

# Configuration de la base de données SQLite
DATABASE = "db.sqlite3"

# Modèles Pydantic
class PostCreate(BaseModel):
    title: str
    resume: str
    content: str
    views: int
    image: str
    publish: bool = True

class Comment(BaseModel):
    id: int
    author: str
    message: str
    created_at: datetime
    post_id: int


class Post(BaseModel):
    id: int
    title: str
    resume: str
    content: str
    views: int
    image: str
    publish: bool
    created_at: datetime
    comments: List[Comment] = []


class CommentCreate(BaseModel):
    author: str
    message: str
    post_id: int


# Fonctions d'aide pour interagir avec la base de données
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            resume TEXT NOT NULL,
            content TEXT NOT NULL,
            views INTEGER NOT NULL,
            image TEXT NOT NULL,
            publish BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN NOT NULL DEFAULT 1,
            post_id INTEGER NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    """)
    conn.commit()
    conn.close()


create_tables()


app = FastAPI()

app.mount("/images/", StaticFiles(directory="images"))

@app.get("/", response_model=List[Post])
@app.get("/api/", response_model=List[Post])
@app.get("/api/posts/", response_model=List[Post])
async def post_list(request: Request):
    conn = get_db()
    cursor = conn.cursor()
    # Récupérer toutes les publications publiées
    cursor.execute("SELECT * FROM posts WHERE publish = 1")
    posts = cursor.fetchall()
    
    posts_list = []
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    for post in posts:
        post_dict = dict(post)
        
        # Construire l'URL complète pour l'image
        image_url = f"{base_url}/images/{post_dict['image']}"
        post_dict["image"] = image_url
        
        # Récupérer les commentaires associés à chaque publication
        cursor.execute("SELECT * FROM comments WHERE post_id = ?", (post["id"],))
        comments = cursor.fetchall()
        post_dict["comments"] = [Comment(**dict(comment)) for comment in comments]
        
        # Créer un modèle Post avec les commentaires
        posts_list.append(Post(**post_dict))
    
    conn.close()
    return posts_list


@app.get("/api/posts/{post_id}/", response_model=Post)
async def post_detail(request: Request, post_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    # Récupérer la publication spécifiée par ID
    cursor.execute("SELECT * FROM posts WHERE publish=1 AND id = ?", (post_id,))
    post = cursor.fetchone()
    if post is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Récupérer les commentaires associés
    cursor.execute("SELECT * FROM comments WHERE post_id = ?", (post_id,))
    comments = cursor.fetchall()
    conn.close()

    post_dict = dict(post)
    
    # Construire l'URL complète pour l'image
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    image_url = f"{base_url}/images/{post_dict['image']}"
    post_dict["image"] = image_url
    
    # Ajouter les commentaires au dictionnaire
    post_dict["comments"] = [Comment(**dict(comment)) for comment in comments]
    
    return Post(**post_dict)


@app.post("/api/posts/create/", response_model=Post)
def create_post(post: PostCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (title, resume, content, views, image, publish, created_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (post.title, post.resume, post.content, post.views, post.image, post.publish))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    return Post(id=post_id, **post.dict(), created_at=datetime.now())

@app.put("/api/posts/{post_id}/", response_model=Post)
def update_post(post_id: int, updated_post: PostCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if post is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    cursor.execute(
        """
        UPDATE posts
        SET title = ?, resume = ?, content = ?, views = ?, image = ?, publish = ?
        WHERE id = ?
        """, (updated_post.title, updated_post.resume, updated_post.content, updated_post.views, updated_post.image, updated_post.publish, post_id))
    conn.commit()
    conn.close()
    return Post(id=post_id, **updated_post.dict(), created_at=post["created_at"])

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return {"detail": "Post deleted"}


@app.post("/api/comments/create/", response_model=Comment)
def create_comment(comment: CommentCreate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (comment.post_id,))
    post = cursor.fetchone()
    if post is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    cursor.execute(
        """
          INSERT INTO comments (author, message, post_id, created_at)
          VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (comment.author, comment.message, comment.post_id))
    conn.commit()
    comment_id = cursor.lastrowid
    conn.close()
    return Comment(id=comment_id, **comment.dict(), created_at=datetime.now())

