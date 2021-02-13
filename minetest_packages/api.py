"""
Searches, fetches and loads Minetest packages
from an online ContentDB.
"""

import typing
import urllib.parse

import anyjson  # type: ignore
import attr
import requests

from . import package

SelfSearchItem = typing.TypeVar("SelfSearchItem", bound="SearchItem")


@attr.s(auto_attribs=True)
class OnlineContent:
    """An online ContentDB provider."""

    base_address: str

    def make_url(self, *components: str):
        """Join a full URL from the base address and components."""
        return urllib.parse.urljoin(
            self.base_address, "/".join(urllib.parse.quote(x) for x in components)
        )

    def search_url(self, query: str):
        """Makes a ContentDB API search URL from a query string."""
        return self.make_url("api/packages" "?q=" + query)

    def package_url(self, author: str, name: str):
        """Makes a ContentDB API package info URL from a package name and author."""
        return self.make_url("api/packages", author, name)

    def search(self, query: str) -> "Search":
        """Uses the online API to search for packages matching a query."""
        response = requests.get(self.search_url(query))
        return Search.parse(self, response.text)

    def fetch(self, author: str, name: str) -> package.Package:
        """Fetch a Minetest mod definition from the author and name, through
        the online API."""
        response = requests.get(self.package_url(author, name))
        return package.Package.parse(response.text)

minetest_contentdb = OnlineContent("https://content.minetest.net")


class SearchItemDefs(typing.Protocol):
    """The JSON definitions returned by the ContentDB API package search endpoint."""

    @typing.overload
    def __getitem__(self, x: typing.Literal["author"]) -> str:
        """Author of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(self, x: typing.Literal["name"]) -> str:
        """Name of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(self, x: typing.Literal["release"]) -> int:
        """Release of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(self, x: typing.Literal["short_description"]) -> str:
        """Short description of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(self, x: typing.Literal["title"]) -> str:
        """Title description of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(
        self, x: typing.Literal["package_type"]
    ) -> typing.Literal["game", "mod", "txp"]:
        """Type of a package under a search item."""
        ...

    @typing.overload
    def __getitem__(self, x: typing.Literal["thumbnail"]) -> str:
        """Thumbnail image address of a package under a search item."""
        ...

    def __getitem__(self, x: str) -> typing.Any:
        """Gets a field from this JSON field collection of a search item."""
        ...


@attr.s(auto_attribs=True)
class SearchItem:
    """A search result from a Minetest API search query."""

    content_db: OnlineContent
    author: str
    name: str
    release: int
    short_description: str
    title: str
    package_type: typing.Literal["game", "mod", "txp"]
    thumbnail: str

    def fetch(self):
        """Returns a full MinetestPackage definition, by
        fetching it by author and name."""
        return self.content_db.fetch(self.author, self.name)

    @classmethod
    def parse(
        cls: typing.Type[SelfSearchItem],
        content_db: OnlineContent,
        defs: SearchItemDefs,
    ) -> SelfSearchItem:
        """Makes a MinetestSearchItem by parsing a collection of fields."""
        return cls(
            content_db,
            defs["author"],
            defs["name"],
            defs["release"],
            defs["short_description"],
            defs["title"],
            defs["package_type"],
            defs["thumbnail"],
        )


@attr.s(auto_attribs=True)
class Search:
    """A Minetest API search query."""

    content_dbdb: OnlineContent
    items: typing.Dict[typing.Tuple[str, str], SearchItem]

    @classmethod
    def parse(cls, content_db: OnlineContent, document: str):
        """Parses a search result JSON string from a ContentDB API search endpoint."""
        items = {}

        for mdef in anyjson.loads(document):
            items[mdef["author"], mdef["name"]] = SearchItem.parse(content_db, mdef)

        return cls(content_db, items)

    def find(self, author: str, name: str) -> typing.Optional[SearchItem]:
        """Finds a search item that matches the given author and name, if it exists."""
        if (author, name) in self.items:
            return self.items[author, name]

        return None

    def all_items(self) -> typing.Generator[SearchItem, None, None]:
        """Iterate on all search items of this search query"""
        for item in self.items.values():
            yield item
