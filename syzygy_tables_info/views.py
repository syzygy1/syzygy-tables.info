# This file is part of the syzygy-tables.info tablebase probing website.
# Copyright (C) 2015-2020 Niklas Fiekas <niklas.fiekas@backscattering.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import textwrap

import chess

import syzygy_tables_info.stats

from syzygy_tables_info.model import ColorName, Render, RenderMove, RenderStats, DEFAULT_FEN
from tinyhtml import Frag, html, h, frag, raw
from typing import Optional


def asset_url(path: str) -> str:
    return "/static/{}?mtime={}".format(path, os.path.getmtime(os.path.join(os.path.dirname(__file__), "..", "static", path)))


def fen_url(fen: str) -> str:
    return f"/?fen={fen.replace(' ', '_')}"


def kib(num: float) -> str:
    for unit in ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB"]:
        if abs(num) < 1024:
            return "%3.1f %s" % (num, unit)
        num /= 1024
    return "%.1f %s" % (num, "Yi")


def layout(*, title: str, development: bool, left: Optional[Frag] = None, right: Optional[Frag] = None, head: Optional[Frag] = None, scripts: Optional[Frag] = None) -> Frag:
    return html(lang="en")(
        raw("<!-- https://github.com/niklasf/syzygy-tables.info -->"),
        h("head")(
            h("meta", charset="utf-8"),
            h("link", rel="preload", href="/static/fonts/fontello.woff2", as_="font", type="font/woff2", crossorigin=True),
            h("link", rel="stylesheet", href=asset_url("css/style.min.css")),
            head,
            h("title")(title, " – Syzygy endgame tablebases"),
            h("meta", name="viewport", content="width=device-width,initial-scale=1.0,user-scalable=yes"),
            h("meta", name="keywords", content="Syzygy,chess,endgame,tablebase"),
            h("meta", name="author", content="Niklas Fiekas"),
            h("link", rel="author", title="Legal", href="/legal"),
            h("link", rel="icon", href="/static/favicon.32.png", type="image/png", sizes="32x32"),
            h("link", rel="icon", href="/static/favicon.64.png", type="image/png", sizes="64x64"),
            h("link", rel="icon", href="/static/favicon.96.png", type="image/png", sizes="96x96"),
            h("link", rel="sitemap", href="/sitemap.txt", type="text/plain"),
        ),
        h("body")(
            h("div", style="background:#c00;color:#fff;text-align:center;font-weight:bold;position:fixed;z-index:1;width:100%;top:0;")("Careful, this is an unreliable development version") if development else None,
            h("div", klass="left-side")(
                h("div", klass="inner")(left),
            ),
            h("div", klass="right-side")(
                h("div", klass="inner")(right),
            ),
            h("footer")(
                h("div", klass="inner")(
                    h("p")(
                        "Powered by Ronald de Man's ",
                        h("a", href="https://github.com/syzygy1/tb")("Syzygy endgame tablebases"), ", ",
                        "7-piece tables generated by Bojun Guo and a ",
                        h("a", href="https://github.com/niklasf/lila-tablebase#http-api")("public API"), " ",
                        "hosted by ",
                        h("a", href="https://tablebase.lichess.ovh")("lichess.org"), ".",
                    ),
                    h("p")(
                        h("a", href="/endgames")("Endgames"), ". ",
                        h("a", href="/metrics")("Metrics"), ". ",
                        h("a", href="/legal", data_jslicense=1)("Legal"), ". ",
                        h("a", href="https://github.com/niklasf/syzygy-tables.info")("GitHub"), ". ",
                    ),
                ),
            ),
            scripts,
        ),
    )


def index(*, development: bool = True, render: Render) -> Frag:
    def spare(color: ColorName) -> Frag:
        return h("div", klass=["spare", "bottom" if color == "white" else "top"])(
            frag(
                h("piece", klass=[color, role], data_color=color, data_role=role)(),
                " ",
            ) for role in ["pawn", "knight", "bishop", "rook", "queen", "king"]
        )

    return layout(
        development=development,
        title=render["material"],
        head=frag(
            h("meta", name="description", content="User interface and public API for probing Syzygy endgame tablebases"),
            h("meta", property="og:image", content=render["thumbnail_url"]),
            h("meta", property="twitter:image", content=render["thumbnail_url"]),
        ),
        left=frag(
            h("h1", klass="main")(
                h("a", href="/")("Syzygy endgame tablebases"),
            ),
            h("nav")(
                h("div", id="side-to-move-toolbar")(
                    h("div", id="side-to-move", klass="btn-group", role="group", aria_label="Side to move")(
                        h("a", klass={
                            "btn": True,
                            "btn-default": True,
                            "active": render["turn"] == "white",
                        }, id="btn-white", href=fen_url(render["white_fen"]))("White to move"),
                        h("a", klass={
                            "btn": True,
                            "btn-default": True,
                            "active": render["turn"] == "black",
                        }, id="btn-black", href=fen_url(render["black_fen"]))("Black to move"),
                    ),
                    " ",
                    h("div", klass="btn-group")(
                        h("button", id="btn-edit", klass="btn btn-default", title="Edit mode: Do not switch sides when playing moves")(
                            h("span", klass="icon icon-lock-open")(),
                        ),
                    ),
                ),
                spare("black"),
                h("div", id="board", data_fen=render["fen"])(
                    h("noscript")("JavaScript required for interactive board view."),
                ),
                spare("white"),
                h("div", id="board-toolbar", role="toolbar")(
                    h("div", klass="btn-group")(
                        h("button", id="btn-flip-board", klass="btn btn-default", title="Flip board")(
                            h("span", klass="icon icon-rotate")(),
                        ),
                    ),
                    " ",
                    h("div", klass="btn-group")(
                        h("a", id="btn-clear-board", href=fen_url(render["clear_fen"]), klass="btn btn-default", title="Clear board")(
                            h("span", klass="icon icon-eraser")(),
                        ),
                    ),
                    " ",
                    h("div", klass="btn-group")(
                        h("a", id="btn-swap-colors", href=fen_url(render["swapped_fen"]), klass="btn btn-default", title="Swap colors")(
                            h("span", klass="icon icon-black-white")(),
                        ),
                        h("a", id="btn-mirror-horizontal", href=fen_url(render["horizontal_fen"]), klass="btn btn-default", title="Mirror horizontally")(
                            h("span", klass="icon icon-horizontal")(),
                        ),
                        h("a", id="btn-mirror-vertical", href=fen_url(render["vertical_fen"]), klass="btn btn-default", title="Mirror vertically")(
                            h("span", klass="icon icon-vertical")(),
                        ),
                    ),
                ),
                h("form", id="form-set-fen", action="/")(
                    h("div", klass="input-group")(
                        h("input", id="fen", name="fen", type="text", value=render["fen_input"], klass="form-control", aria_label="FEN", placeholder=DEFAULT_FEN),
                        h("span", klass="input-group-btn")(
                            h("input", type="submit", klass="btn btn-default", value="Set FEN"),
                        ),
                    ),
                ),
            ),
        ),
        right=xhr_probe(render),
        scripts=h("script", src=asset_url("js/client.min.js"), async_=True, defer=True)(),
    )


def xhr_probe(render: Render) -> Frag:
    def move(m: RenderMove) -> Frag:
        return h("a", klass="li", href=fen_url(m["fen"]), data_uci=m["uci"])(
            m["san"],
            h("span", klass="badge")(f"DTM {m['dtm']}") if m["dtm"] else None,
            h("span", klass="badge")(m["badge"]),
        )

    middot = raw(" &middot ")

    stats = render["stats"]

    return h("section")(
        # Status.
        h("h2", id="status", klass=[
            f"{render['winning_side']}-win" if render["winning_side"] else None,
            "frustrated" if render["frustrated"] else None,
        ])(render["status"]),

        # Move lists.
        h("div", id="winning", klass=f"list-group {render['turn']}-turn")(
            move(m) for m in render["winning_moves"]
        ),
        h("div", id="unknown", klass="list-group")(
            move(m) for m in render["unknown_moves"]
        ),
        h("div", id="cursed", klass=f"list-group {render['turn']}-turn")(
            move(m) for m in render["cursed_moves"]
        ),
        h("div", id="drawing", klass="list-group")(
            move(m) for m in render["drawing_moves"]
        ),
        h("div", id="blessed", klass=f"list-group {render['turn']}-turn")(
            move(m) for m in render["blessed_moves"]
        ),
        h("div", id="losing", klass=f"list-group {render['turn']}-turn")(
            move(m) for m in render["losing_moves"]
        ),

        # Info.
        h("div", id="info")(
            h("p")(
                "The given position is not a legal chess position."
            ) if render["illegal"] else h("p")(
                h("strong")("The game is drawn"),
                " because with the remaining material no sequence of legal moves can lead to checkmate."
            ) if render["insufficient_material"] else frag(
                h("p")(
                    h("a", href="https://en.wikipedia.org/wiki/Solving_chess")("Chess is not yet solved."),
                ) if render["fen"] == chess.STARTING_FEN else None,
                h("p")("Syzygy tables only provide information for positions with up to 7 pieces and no castling rights."),
            ) if render["unknown_moves"] else h("p")(
                h("strong")("This is a blessed loss."),
                " Mate can be forced, but a draw can be achieved under the fifty-move rule.",
            ) if render["blessed_loss"] else h("p")(
                h("strong")("This is a cursed win."),
                " Mate can be forced, but a draw can be achieved under the fifty-move rule.",
            ) if render["cursed_win"] else None,
        ),
        frag(
            h("a", klass="meta-link", href=f"/syzygy-vs-syzygy/{render['material']}.pgn?fen={render['fen'].replace(' ', '_')}", title="Download DTZ mainline")(
                h("span", klass="icon icon-download", aria_hidden="true")(),
                f" {render['material']}.pgn",
            ),
            " ",
            h("a", klass="meta-link", href=f"https://lichess.org/analysis/standard/{render['fen'].replace(' ', '_')}#explorer")(
                h("span", klass="icon icon-external", aria_hidden="true")(),
                " lichess.org",
            ),
        ) if not render["illegal"] else None,

        # Stats.
        section_stats(render, stats) if stats else None,

        # Dependencies.
        h("section", id="dependencies")(
            h("h3")(f"{render['material']} dependencies"),
            frag(
                h("p")(f"To probe all {render['normalized_material']} positions, these tables and their transitive dependencies are also required:"),
                h("p")(
                    frag(
                        middot if i > 0 else None,
                        h("a", href=fen_url(dep["longest_fen"]))(dep["material"]),
                    ) for i, dep in enumerate(render["deps"])
                )
            ) if render["deps"] else None,
            h("p")(
                h("a", klass="meta-link", href=f"/download/{render['normalized_material']}.txt?source=lichess&dtz=root", title="Download list")(
                    h("span", klass="icon icon-list", aria_hidden="true")(),
                    f" {render['normalized_material']}.txt",
                ),
                " ",
                h("a", klass="meta-link", href=f"/graph/{render['normalized_material']}.dot", title="Dependency graph")(
                    h("span", klass="icon icon-graph", aria_hidden="true")(),
                    f" {render['normalized_material']}.dot",
                ),
            ),
        ) if render["is_table"] else None,

        # Homepage.
        frag(
            h("section", id="syzygy")(
                h("h2")("Syzygy tablebases"),

                h("h3")("About"),
                h("p")(
                    "Syzygy tablebases allow perfect play with up to 7 pieces, ",
                    "both with and without the fifty-move drawing rule, ",
                    "i.e., they allow winning all won ",
                    "positions and bringing all drawn positions over the fifty-move line.",
                ),
                h("p")(
                    "The tables provide ",
                    h("a", href="/metrics")(wdl50, " and ", dtz50_pp, " information"),
                    ". ",
                    "Forcing captures or pawn moves while keeping a win in hand ",
                    "ensures that progress is being made.",
                ),
                h("p")(
                    "DTZ optimal play is not always the shortest way to mate ",
                    "(", h("abbr", title="depth-to-mate")("DTM"), ") ",
                    "and can even look unintuitive: ",
                    "For example sometimes pieces can be sacrificed to reset the fifty-move ",
                    "counter as soon as possible. However, unlike DTM it achieves the best ",
                    "possible result even with the fifty-move rule.",
                ),
                h("p")(
                    "6-piece tables were ",
                    h("a", href="http://www.talkchess.com/forum3/viewtopic.php?t=47681")("released"),
                    " by Ronald de Man in April 2013, including ",
                    h("a", href="https://github.com/syzygy1/tb")("probing code and the generator"),
                    ".",
                ),
                h("p")(
                    "From May to August 2018 Bojun Guo ",
                    h("a", href="http://www.talkchess.com/forum/viewtopic.php?start=0&t=66797&topic_view=flat")("generated"),
                    " 7-piece tables. ",
                    "The 7-piece tablebase contains 423,836,835,667,331 ",
                    h("a", href="https://kirill-kryukov.com/chess/nulp/results.html")("unique legal positions"),
                    " in about 18 Terabytes.",
                ),

                h("h3")("Selected positions"),
                h("ul")(
                    h("li")(
                        h("a", href="/endgames")("Longest endgames"), ": ",
                        h("a", href="/?fen=8/8/8/8/8/8/2Rk4/1K6_b_-_-_0_1")("3"), ", ",
                        h("a", href="/?fen=8/8/8/6B1/8/8/4k3/1K5N_b_-_-_0_1")("4"), ", ",
                        h("a", href="/?fen=K7/N7/k7/8/3p4/8/N7/8_w_-_-_0_1")("5"), ", ",
                        h("a", href="/?fen=6N1/5KR1/2n5/8/8/8/2n5/1k6_w_-_-_0_1")("6"), ", ",
                        h("a", href="/?fen=QN4n1/6r1/3k4/8/b2K4/8/8/8_b_-_-_0_1")("7 pieces"),
                    ),
                    h("li")(
                        h("a", href="/?fen=8/6B1/8/8/B7/8/K1pk4/8_b_-_-_0_1")("Black escapes to a blessed loss with an underpromotion"),
                    ),
                    h("li")(
                        h("a", href="/?fen=k7/2QR4/8/8/8/4N3/2r4Q/1K6_b_-_-_0_1")("Black rook chasing king to force stalemate, without avail"),
                    ),
                    h("li")(
                        h("a", href="/?fen=6B1/3B4/5R2/6q1/P7/1k6/8/3K4_b_-_-_0_1")("656 half-moves before the winning side can safely move a pawn"),
                    ),
                ),
            ),
            h("section", id="download")(
                h("h2")("Download"),
                h("p")(
                    "If you want to use tablebases in a chess engine you certainly need a local copy."
                ),
                h("p")(
                    "Most of the time (during search) only WDL tables are used. ",
                    "Keep these on SSD storage if you can. ",
                    "DTZ tables are generally only used to finish the final phase of the game (\"at the root\").",
                ),
                h("table")(
                    h("thead")(
                        h("tr")(
                            h("th")("Pieces"),
                            h("th")("WDL"),
                            h("th")("DTZ"),
                            h("th")("Total"),
                        ),
                    ),
                    h("tbody")(
                        h("tr")(
                            h("td")("3-5"),
                            h("td")(kib(387124)),
                            h("td")(kib(574384)),
                            h("td")(kib(961508)),
                        ),
                        h("tr")(
                            h("td")("6"),
                            h("td")(kib(71127940)),
                            h("td")(kib(85344200)),
                            h("td")(kib(156472140)),
                        ),
                        h("tr")(
                            h("td")("7"),
                            h("td")(kib(9098389892)),
                            h("td")(kib(8859535148)),
                            h("td")(kib(17957925040)),
                        ),
                    ),
                ),
                h("p")(
                    h("a", href="https://github.com/syzygy1/tb")("Generating"),
                    " the tablebases requires considerable computational resources. ",
                    "It is more efficient to download them from a mirror:",
                ),
                h("table")(
                    h("thead")(
                        h("tr")(
                            h("th")("Host"),
                            h("th")("Info"),
                            h("th")("List"),
                        ),
                    ),
                    h("tbody")(
                        h("tr")(
                            h("td")(h("a", href="http://tablebase.sesse.net/")("tablebase.sesse.net")),
                            h("td")("http, EU"),
                            h("td")(h("a", href="/download.txt?source=sesse&max-pieces=7", title="List of URLs (txt)")(h("span", klass="icon icon-list")())),
                        ),
                        h("tr")(
                            h("td")(h("a", href="https://tablebase.lichess.ovh/tables/")("tablebase.lichess.ovh")),
                            h("td")("http, https, EU"),
                            h("td")(h("a", href="/download.txt?source=lichess&max-pieces=7", title="List of URLs (txt)")(h("span", klass="icon icon-list")())),
                        ),
                        h("tr")(
                            h("td")(h("a", href="https://ipfs.syzygy-tables.info/")("ipfs.syzygy-tables.info")),
                            h("td")("ipfs, Cloudflare"),
                            h("td")(h("a", href="/download.txt?source=ipfs&max-pieces=7", title="List of URLs (txt)")(h("span", klass="icon icon-list")())),
                        ),
                    ),
                ),
                h("h3")("Checksums"),
                h("a", href="/checksums/bytes.tsv", title="du --bytes")("file sizes"), middot,
                h("a", href="/checksums/tbcheck.txt", title="Internal non-cryptographic checksums")("tbcheck"), middot,
                h("a", href="/checksums/md5")("md5"), middot,
                h("a", href="/checksums/sha1")("sha1"), middot,
                h("a", href="/checksums/sha256")("sha256"), middot,
                h("a", href="/checksums/sha512")("sha512"), middot,
                h("a", href="/checksums/b2")("blake2"), middot,
                h("a", href="/checksums/PackManifest", title="PackManifest")("ipfs"),
            ),
            h("section", id="contact")(
                h("h2")("Contact"),
                h("p")(
                    "Feedback ",
                    h("a", href="/legal#contact")("via mail"),
                    ", bug reports and ",
                    h("a", href="https://github.com/niklasf/syzygy-tables.info")("pull requests"),
                    " are welcome."
                ),
            ),
        ) if render["fen"] == DEFAULT_FEN else None,
    )


def section_stats(render: Render, stats: RenderStats) -> Frag:
    return h("section", id="stats")(
        frag(
            h("h3")(
                f"Histogram: {stats['material_side']} {stats['verb']} vs. {stats['material_other']} ",
                raw("(log&nbsp;scale)"),
            ),
            h("div", klass="histogram")(
                (
                    h(
                        "div",
                        klass="empty",
                        title=f"{row['empty']} empty rows skipped",
                    )("⋮") if row["empty"] else h(
                        "div",
                        style=f"width:{row['width']}%;",
                        klass="active" if row["active"] else None,
                        title=f"{row['num']:,} unique positions with {stats['material_side']} {stats['verb']} in {row['ply']} (DTZ)"
                    )()
                ) for row in stats["histogram"]
            ),
        ) if stats.get("histogram") else None,

        frag(
            h("h3")(f"Longest {render['material']} phases"),
            h("ul")(
                h("li")(
                    h("a", href=fen_url(longest["fen"]))(longest["label"]),
                ) for longest in stats["longest"]
            ),
        ) if stats["longest"] else None,

        h("h3")(f"{render['material']} statistics (unique positions)"),
        h("div", klass="list-group stats")(
            h("div", klass="li white-win", title="Unique positions with white wins")(
                "White wins:",
                h("br"),
                f"{stats['white']:,} ({stats['white_pct']}%)"
            ) if stats["white"] else None,
            h("div", klass="li white-win frustrated", title="Unique positions with frustrated white wins")(
                "Frustrated white wins:",
                h("br"),
                f"{stats['cursed']:,} ({stats['cursed_pct']}%)"
            ) if stats["cursed"] else None,
            h("div", klass="li draws", title="Unique drawn positions")(
                "Draws:",
                h("br"),
                f"{stats['draws']:,} ({stats['draws_pct']}%)"
            ) if stats["draws"] else None,
            h("div", klass="li black-win frustrated", title="Unique positions with frustrated black wins")(
                "Frustrated black wins:",
                h("br"),
                f"{stats['blessed']:,} ({stats['blessed_pct']}%)"
            ) if stats["blessed"] else None,
            h("div", klass="li black-win", title="Unique positions with black wins")(
                "Black wins:",
                h("br"),
                f"{stats['black']:,} ({stats['black_pct']}%)"
            ) if stats["black"] else None,
        ),

        h("a", href=f"/stats/{render['material']}.json", title=f"Machine readable endgame statistics for {render['material']}")(
            h("span", klass="icon icon-stats", aria_hidden="true")(),
            f" {render['material']}.json ",
            h("a", href="/stats")("(?)"),
        ),
    )


def back_to_board() -> Frag:
    return h("nav")(
        h("div", klass="reload")(
            h("a", klass="btn btn-default", href="/")("Back to board"),
        ),
    )


def legal(*, development: bool = True) -> Frag:
    return layout(
        development=development,
        title="Legal",
        left=frag(
            h("h1")("Legal"),
            h("p")("The tablebase lookup is provided on a best-effort basis, without guarantees of correctness or availability. Feedback or questions are welcome."),
            h("p")("Records no personal information other than standard server logs. The logs are kept no longer than 48 hours."),
            back_to_board(),
        ),
        right=frag(
            h("section", id="contact")(
                h("h2")("Contact"),
                h("p")(
                    h("a", href="mailto:niklas.fiekas@backscattering.de")("niklas.fiekas@backscattering.de"), " ",
                    "(", h("a", href="https://pgp.mit.edu/pks/lookup?op=get&search=0x2ECA66C65B255138")("pgp"), ")",
                ),
            ),
            h("section", id="thanks")(
                h("h2")("Software licenses"),
                h("p")(
                    "The ",
                    h("a", href="https://github.com/niklasf/syzygy-tables.info")("code for the website itself"),
                    " is ",
                    h("a", href="https://github.com/niklasf/syzygy-tables.info/blob/master/LICENSE")("licensed under the AGPL-3.0+"),
                    ".",
                ),
                h("table", id="jslicense-labels1")(
                    h("thead")(
                        h("tr")(
                            h("th")("Script"),
                            h("th")("License"),
                            h("th")("Source"),
                        ),
                    ),
                    h("tbody")(
                        h("tr")(
                            h("td")(
                                h("a", href=asset_url("js/client.min.js"))("client.min.js"),
                            ),
                            h("td")(
                                h("a", href="https://www.gnu.org/licenses/agpl-3.0.en.html")("AGPL-3.0+"),
                            ),
                            h("td")(
                                h("a", href="https://github.com/niklasf/syzygy-tables.info/blob/master/src/client.ts")("client.ts"),
                            ),
                        ),
                    ),
                ),
                h("p")("It also uses the following software/artwork:"),
                h("ul")(
                    h("li")(
                        h("a", href="https://github.com/ornicar/chessground")("chessground"),
                        " (GPL-3.0+)",
                    ),
                    h("li")(
                        h("a", href="https://github.com/niklasf/chessops")("chessops"),
                        " (GPL-3.0+)",
                    ),
                    h("li")(
                        h("a", href="https://github.com/niklasf/python-chess")("python-chess"),
                        " (GPL-3.0+)",
                    ),
                    h("li")(
                        h("a", href="https://github.com/niklasf/python-tinyhtml")("tinyhtml"),
                        " (MIT/Apache-2.0)",
                    ),
                    h("li")(
                        h("a", href="http://aiohttp.readthedocs.org/en/stable/")("aiohttp"),
                        " (Apache-2.0)",
                    ),
                    h("li")(
                        "Selected icons from ",
                        h("a", href="https://fontawesome.com/")("Font Awesome"),
                        " (SIL)",
                    ),
                    h("li")(
                        "A few styles from ",
                        h("a", href="https://getbootstrap.com/")("Bootstrap"),
                        " (MIT)",
                    ),
                ),
            ),
        ),
    )


wdl50 = frag("WDL", h("sub")(50))
dtz50_pp = frag("DTZ", h("sub")(50), "′′")


def metrics(*, development: bool) -> Frag:
    n = h("var")("n")
    example1 = "1kb5/8/1KN5/3N4/8/8/8/8 b - -"
    example2 = "8/8/2N5/8/3k4/7N/p2K4/8 b - -"

    def example_board(epd: str, check: str) -> Frag:
        board_fen = epd.split(" ")[0]
        return h("a", href=f"/?fen={epd.replace(' ', '_')}_0_1")(
            h("img", width=300, height=300, alt=epd, src=f"https://backscattering.de/web-boardimage/board.svg?fen={board_fen}&check={check}"),
        )

    def example_link(epd: str) -> Frag:
        return h("a", href=f"/?fen={epd.replace(' ', '_')}_0_1")(epd)

    return layout(
        development=development,
        title="Metrics",
        left=frag(
            h("h1")("Metrics"),
            h("p")("Information stored in Syzygy tablebases"),
            back_to_board(),
        ),
        right=frag(
            h("section", id="wdl")(
                h("h2")(wdl50),
                h("p")(
                    "5-valued ",
                    h("em")("Win/Draw/Loss"),
                    " information can be used to decide which positions to aim for.",
                ),
                h("div", klass="list-group stats")(
                    h("div", klass="li white-win")("Win (+2)"),
                    h("div", klass="li white-win frustrated")("Win prevented by 50-move rule (+1)"),
                    h("div", klass="li draws")("Drawn (0)"),
                    h("div", klass="li black-win frustrated")("Loss saved by 50-move rule (-1)"),
                    h("div", klass="li black-win")("Loss (-2)"),
                ),
            ),
            h("section", id="dtz")(
                h("h2")(dtz50_pp, " with rounding"),
                h("p")(
                    "Once a tablebase position has been reached, the ",
                    h("em")("Distance To Zeroing"), " ",
                    "(of the fifty-move counter by a capture or pawn move) ",
                    "can be used to reliably make progress in favorable positions and stall ",
                    "in unfavorable positions.",
                ),
                h("p")("The precise meanings are as follows:"),
                h("p")(
                    "A DTZ value ", n, " with 100 ≥ ", n, " ≥ 1 means the position is winning, ",
                    "and a zeroing move or checkmate can be forced in ", n, " or ", n, " + 1 half-moves.",
                ),
                example_board(example1, "b8"),
                h("p")(
                    "For an example of this ambiguity, see how the DTZ repeats after the only-move Ka8 in ",
                    example_link(example1), ". ",
                    "This is due to the fact that some Syzygy tables store rounded moves ",
                    "instead of half-moves, to save space. This implies some primary tablebase lines ",
                    "may waste up to 1 ply. Rounding is never used for endgame phases where it would ",
                    "change the game theoretical outcome (", wdl50, ").",
                ),
                h("p")(
                    "Users need to be careful in positions ",
                    "that are nearly drawn under ",
                    "the 50-move rule! Carelessly wasting 1 more ply ",
                    "by not following the tablebase recommendation, for a total of 2 wasted plies, ",
                    "may change the outcome of the game.",
                ),
                h("p")(
                    "A DTZ value ", n, " > 100 means the position is winning, but drawn under the 50-move rule. ",
                    "A zeroing move or checkmate can be forced in ", n, " or ", n, " + 1 half-moves, ",
                    "or in ", n, " - 100 or ", n, " + 1 - 100 half-moves ",
                    "if a later phase is responsible for the draw.",
                ),
                example_board("8/8/2N5/8/3k4/7N/p2K4/8 b - -", "d4"),
                h("p")(
                    "For example, in ", example_link(example2), " ",
                    "black promotes the pawn in 7 ply, but the DTZ is 107, ",
                    "indicating that white can hold a draw under the 50-move rule ",
                    "in a later phase of the endgame.",
                ),
                h("p")(
                    "An in-depth discussion of rounding can be found in ",
                    h("a", href="http://www.talkchess.com/forum3/viewtopic.php?f=7&t=58488#p651293")("this thread"), ".",
                ),
            ),
        ),
    )


def stats(*, development: bool) -> Frag:
    return layout(
        development=development,
        title="Machine readable endgame statistics",
        left=frag(
            h("h1")("Machine readable endgame statistics"),
            back_to_board(),
        ),
        right=frag(
            h("section", id="api")(
                h("h2")("API"),
                h("div", klass="panel panel-default")(
                    h("div", klass="panel-heading")(
                        "GET ", h("a", href="/stats.json")("/stats.json"),
                    ),
                    h("div", klass="panel-body")(
                        "All endgame stats with keys such as ", h("code")("KRNvKNN"), ".",
                    ),
                ),
                h("div", klass="panel panel-default")(
                    h("div", klass="panel-heading")(
                        "GET ", h("a", href="/stats/KRNvKNN.json")("/stats/KRNvKNN.json"),
                    ),
                    h("div", klass="panel-body")(
                        "Endgame stats for a specific endgame, e.g., ", h("code")("KRNvKNN"), ". ",
                        "Redirects to normalized endgame names.",
                    ),
                ),
            ),
            h("section", id="example")(
                h("h2")("Example (KRNvKNN)"),
                h("pre")(
                    h("code")(textwrap.dedent("""\
                        {
                          "rtbw": {
                            "bytes": 290002640, // file size
                            "tbcheck": "a320ac...", // internal checksum
                            "md5": "6ee435...",
                            "sha1": "07a0e4...",
                            "sha256": "f3386d...",
                            "sha512": "c4bf73...",
                            "b2": "b970e0...", // blake 2
                            "ipfs": "QmXW4S..."
                          },
                          "rtbz": {
                            // ...
                          },
                          "longest": [
                            // longest winning endgames for black/white
                            // with/without 50-move rule
                            {
                              "epd": "3n1n2/8/8/8/4R3/8/8/NK1k4 b - -",
                              "ply": 100,
                              "wdl": -2
                            },
                            {
                              "epd": "6k1/5n2/8/8/8/5n2/1RK5/1N6 w - -",
                              "ply": 485,
                              "wdl": 1
                            },
                            {
                              "epd": "8/8/8/8/8/8/N1nk4/RKn5 b - -",
                              "ply": 7,
                              "wdl": 2
                            }
                          ],
                          "histogram": {
                            "white": { // white to move
                              "win": [
                                0,
                                1924310948,
                                35087,
                                363845772,
                                37120,
                                138550471,
                                // ...
                              ]
                              "loss": [
                                98698, // # of positions losing in 0
                                144, // # of positions losing in 1
                                3810, // # of positions losing in 2
                                0, // 3
                                596, // 4
                                0, // 5
                                58 // 6
                              ],
                              "wdl": { // # of positions with each wdl
                                "-2": 0,
                                "-1": 103306,
                                "0": 1333429189,
                                "1": 162344388,
                                "2": 2959977091
                              }
                            },
                            "black": { // black to move
                              // ...
                            },
                          }
                        }"""
                    )),
                ),
            ),
        ),
    )


def endgames(*, development: bool) -> Frag:
    def item(material: str) -> Frag:
        return h("li", klass="maximal" if syzygy_tables_info.stats.is_maximal(material) else None)(
            h("a", href=fen_url(syzygy_tables_info.stats.longest_fen(material)))(
                h("strong")(material) if syzygy_tables_info.stats.is_maximal(material) else material,
            ),
        )

    return layout(
        development=development,
        title="Endgames",
        left=frag(
            h("h1")("Endgames"),
            h("p")(
                "These are the longest endgames (maximum ",
                h("a", href="/metrics")(dtz50_pp),
                ") for each material configuration."
            ),
            h("p")(
                h("a", href="/endgames.pgn")(
                    h("span", klass="icon icon-download")(), " endgames.pgn",
                ),
                " (", kib(4396), ")",
            ),
            back_to_board(),
        ),
        right=frag(
            h("section", id=f"{piece_count}-pieces")(
                h("h2")(piece_count, " pieces"),
                h("ul", klass="endgames")(
                    item(material) for material in syzygy_tables_info.stats.STATS if len(material) == piece_count + 1
                ) if piece_count < 5 else (
                    frag(
                        h("h3")("No pawns" if pawns == 0 else ("1 pawn" if pawns == 1 else f"{pawns} pawns")),
                        h("ul", klass="endgames")(
                            item(material) for material in syzygy_tables_info.stats.STATS if len(material) == piece_count + 1 and material.count("P") == pawns
                        ),
                    ) for pawns in range(0, piece_count - 2 + 1)
                )
            ) for piece_count in range(3, 7 + 1)
        ),
    )
