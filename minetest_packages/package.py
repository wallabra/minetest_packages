"""
"Minetest package definitions.

The Package type allows quickly accessing and
processing a lot of information regarding Minetest
content packages.

The definitions listed here are compatible both
with local mods and online ContentDB content.
"""

import datetime
import typing

import anyjson  # type: ignore
import attr

SelfPackage = typing.TypeVar("SelfPackage", bound="Package")


@attr.s(auto_attribs=True)
class Package:
    """A Minetest package definition."""

    name: str
    author: str
    title: str
    short_description: str
    long_description: str
    repo: str
    provides: list[str]
    release: int
    score: int
    license: str
    created_at: datetime.datetime
    maintainers: list[str]
    website: typing.Optional[str]
    issue_tracker: typing.Optional[str]
    thumbnail: typing.Optional[str]
    screenshots: typing.Optional[typing.List[str]]

    @classmethod
    def parse(cls: typing.Type[SelfPackage], document: str) -> SelfPackage:
        """Parse an API response into a MinetestMod instance."""
        fields = anyjson.loads(document)

        created_at = datetime.datetime.fromisoformat(fields["created_at"])

        return cls(
            fields["name"],
            fields["author"],
            fields["title"],
            fields["short_description"],
            fields["long_description"],
            fields["repo"],
            fields["provides"],
            fields["release"],
            fields["score"],
            fields["license"],
            created_at,
            fields["maintainers"],
            fields["website"],
            fields["issue_tracker"],
            fields["thumbnail"],
            fields["screenshots"],
        )
