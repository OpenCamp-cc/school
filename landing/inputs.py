from typing import List, Optional

from pydantic import BaseModel


class ProfileInput(BaseModel):
    name: Optional[str]
    bio: Optional[str]
    threads_url: Optional[str]
    instagram_url: Optional[str]
    email_url: Optional[str]
    facebook_url: Optional[str]
    youtube_url: Optional[str]
    twitter_url: Optional[str]
    website_url: Optional[str]


class ProfileLinkInput(BaseModel):
    title: str
    url: str


class ProfileCategoryInput(BaseModel):
    title: str
