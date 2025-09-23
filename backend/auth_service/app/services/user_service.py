from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.user import User, UserRole
from typing import Optional

class UserService:
    @staticmethod
    async def get_user_by_uid(db: AsyncSession, uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        result = await db.execute(select(User).where(User.uid == uid))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_phone(db: AsyncSession, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        result = await db.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        uid: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        display_name: Optional[str] = None,
        photo_url: Optional[str] = None,
        role: UserRole = UserRole.CUSTOMER
    ) -> User:
        """Create a new user"""
        user = User(
            uid=uid,
            email=email,
            phone_number=phone_number,
            display_name=display_name,
            photo_url=photo_url,
            role=role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update_user_phone(db: AsyncSession, uid: str, phone_number: str) -> Optional[User]:
        """Update user's phone number"""
        result = await db.execute(select(User).where(User.uid == uid))
        user = result.scalar_one_or_none()
        
        if user:
            user.phone_number = phone_number
            await db.commit()
            await db.refresh(user)
        
        return user
    
    @staticmethod
    async def update_user_role(db: AsyncSession, uid: str, role: UserRole) -> Optional[User]:
        """Update user's role"""
        result = await db.execute(select(User).where(User.uid == uid))
        user = result.scalar_one_or_none()
        
        if user:
            user.role = role
            await db.commit()
            await db.refresh(user)
        
        return user
    
    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        uid: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None,
        display_name: Optional[str] = None,
        photo_url: Optional[str] = None,
        role: UserRole = UserRole.CUSTOMER
    ) -> tuple[User, bool]:
        """Get existing user or create new one. Returns (user, created)"""
        user = await UserService.get_user_by_uid(db, uid)
        
        if user:
            # Update user info if provided
            updated = False
            if email and user.email != email:
                user.email = email
                updated = True
            if display_name and user.display_name != display_name:
                user.display_name = display_name
                updated = True
            if photo_url and user.photo_url != photo_url:
                user.photo_url = photo_url
                updated = True
            
            if updated:
                await db.commit()
                await db.refresh(user)
            
            return user, False
        else:
            user = await UserService.create_user(
                db, uid, email, phone_number, display_name, photo_url, role
            )
            return user, True