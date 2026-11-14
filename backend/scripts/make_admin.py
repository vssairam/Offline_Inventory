"""Grant admin rights to an existing user: python scripts/make_admin.py <email>"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models.user import User


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py <email>")
        return 2
    email = sys.argv[1].strip().lower()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"No user with email {email}")
            return 1
        user.is_admin = True
        user.is_active = True
        db.commit()
        print(f"{email} is now an admin")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
