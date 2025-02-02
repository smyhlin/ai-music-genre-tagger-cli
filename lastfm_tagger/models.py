#!filepath: models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class TagModel(BaseModel):
    """
    Pydantic model for a single tag from Last.fm API.
    """
    name: str = Field(..., description="Name of the tag")
    url: str = Field(..., description="URL of the tag page on Last.fm")
    count: Optional[int] = Field(None, description="Count of the tag, relevant for top tags") # Add count

class TopTagsListModel(BaseModel):
    """
    Pydantic model for the list of top tags in Last.fm API response from track.getTopTags and artist.getTopTags.
    """
    tag: Optional[List[TagModel]] = Field(default_factory=list, description="List of tags")

class TrackGetTopTagsResponse(BaseModel):
    """
    Pydantic model for the full response of track.getTopTags API method from Last.fm.
    """
    toptags: Optional[TopTagsListModel] = Field(None, description="Top tags data, if available")
    error: Optional[int] = Field(None, description="Error code, if an error occurred")
    message: Optional[str] = Field(None, description="Error message, if an error occurred")

class ArtistGetTopTagsResponse(BaseModel):
    """
    Pydantic model for the full response of artist.getTopTags API method from Last.fm.
    """
    toptags: Optional[TopTagsListModel] = Field(None, description="Top tags data, if available")
    error: Optional[int] = Field(None, description="Error code, if an error occurred")
    message: Optional[str] = Field(None, description="Error message, if an error occurred")