"""Unit tests for shared common utilities."""

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import (
    HoverTip,
    TextRun,
    class_name_to_id,
    extract_numeric_symbols,
    extract_tips,
    extract_vars,
    render_text_runs,
    resolve_text,
    split_top_level,
    to_jsonable,
)


def runs(markup, vars=None, changed=None, upgraded=False):
    return render_text_runs(markup, vars or {}, changed or set(), upgraded)


# ---------------------------------------------------------------------------
# class_name_to_id
# ---------------------------------------------------------------------------


class TestClassNameToId(unittest.TestCase):
    def test_cases(self):
        cases = [
            ("BallLightning", "BALL_LIGHTNING"),
            ("StrikeDefect", "STRIKE_DEFECT"),
            ("Abrasive", "ABRASIVE"),
            ("BattleFriendV1", "BATTLE_FRIEND_V1"),
            ("TheAdversaryMkOne", "THE_ADVERSARY_MK_ONE"),
            ("AlchemicalCoffer", "ALCHEMICAL_COFFER"),
            ("OneHpMonster", "ONE_HP_MONSTER"),
            ("ArtOfWar", "ART_OF_WAR"),
        ]
        for class_name, expected in cases:
            with self.subTest(class_name=class_name):
                self.assertEqual(class_name_to_id(class_name), expected)


# ---------------------------------------------------------------------------
# split_top_level
# ---------------------------------------------------------------------------


class TestSplitTopLevel(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(split_top_level("a|b|c"), ["a", "b", "c"])

    def test_nested_braces_not_split(self):
        self.assertEqual(split_top_level("{a|b}|c"), ["{a|b}", "c"])

    def test_no_separator(self):
        self.assertEqual(split_top_level("hello"), ["hello"])

    def test_empty(self):
        self.assertEqual(split_top_level(""), [""])


# ---------------------------------------------------------------------------
# render_text_runs — plain text
# ---------------------------------------------------------------------------


class TestRenderTextRunsPlain(unittest.TestCase):
    def test_plain_text(self):
        self.assertEqual(runs("hello world"), [TextRun(text="hello world")])

    def test_newline_preserved(self):
        self.assertEqual(runs("line one\nline two"), [TextRun(text="line one\nline two")])

    def test_empty(self):
        self.assertEqual(runs(""), [])


# ---------------------------------------------------------------------------
# render_text_runs — BBCode tags
# ---------------------------------------------------------------------------


class TestRenderTextRunsTags(unittest.TestCase):
    def test_gold_tag(self):
        self.assertEqual(runs("[gold]Vigor[/gold]"), [TextRun(text="Vigor", style="gold")])

    def test_blue_tag(self):
        self.assertEqual(runs("[blue]10[/blue]"), [TextRun(text="10", style="blue")])

    def test_red_tag(self):
        self.assertEqual(runs("[red]warning[/red]"), [TextRun(text="warning", style="red")])

    def test_tag_wrapping_var(self):
        self.assertEqual(
            runs("[gold]{X}[/gold]", vars={"X": 5}),
            [TextRun(text="5", source_var="X", style="gold")],
        )

    def test_blue_tag_wrapping_var(self):
        self.assertEqual(
            runs("[blue]{Block}[/blue]", vars={"Block": 10}),
            [TextRun(text="10", source_var="Block", style="blue")],
        )

    def test_tag_with_surrounding_text(self):
        self.assertEqual(
            runs("Gain [gold]Block[/gold]."),
            [TextRun(text="Gain "), TextRun(text="Block", style="gold"), TextRun(text=".")],
        )


# ---------------------------------------------------------------------------
# render_text_runs — variable substitution and diff
# ---------------------------------------------------------------------------


class TestRenderTextRunsVars(unittest.TestCase):
    def test_bare_var(self):
        self.assertEqual(runs("{Damage}", vars={"Damage": 7}), [TextRun(text="7", source_var="Damage")])

    def test_unknown_var_passthrough(self):
        self.assertEqual(runs("{Unknown}"), [TextRun(text="{Unknown}")])

    def test_diff_base_no_style(self):
        self.assertEqual(
            runs("{Damage:diff()}", vars={"Damage": 7}, upgraded=False),
            [TextRun(text="7", source_var="Damage")],
        )

    def test_diff_upgraded_changed_green(self):
        self.assertEqual(
            runs("{Damage:diff()}", vars={"Damage": 10}, changed={"Damage"}, upgraded=True),
            [TextRun(text="10", source_var="Damage", style="green")],
        )

    def test_diff_upgraded_negative_red(self):
        self.assertEqual(
            runs("{Cost:diff()}", vars={"Cost": -1}, changed={"Cost"}, upgraded=True),
            [TextRun(text="-1", source_var="Cost", style="red")],
        )

    def test_diff_upgraded_not_changed_no_style(self):
        self.assertEqual(
            runs("{Damage:diff()}", vars={"Damage": 7}, changed=set(), upgraded=True),
            [TextRun(text="7", source_var="Damage")],
        )


# ---------------------------------------------------------------------------
# render_text_runs — IfUpgraded
# ---------------------------------------------------------------------------


class TestRenderTextRunsIfUpgraded(unittest.TestCase):
    def test_upgraded_shows_first(self):
        self.assertEqual(runs("{IfUpgraded:show:A|B}", upgraded=True), [TextRun(text="A")])

    def test_base_shows_second(self):
        self.assertEqual(runs("{IfUpgraded:show:A|B}", upgraded=False), [TextRun(text="B")])

    def test_no_else_returns_empty_on_base(self):
        self.assertEqual(runs("{IfUpgraded:show:A}", upgraded=False), [])


# ---------------------------------------------------------------------------
# render_text_runs — plural
# ---------------------------------------------------------------------------


class TestRenderTextRunsPlural(unittest.TestCase):
    def test_singular(self):
        # plural selects a plain string branch — source_var is not propagated into the rendered text
        self.assertEqual(
            runs("{Count:plural:time|times}", vars={"Count": 1}),
            [TextRun(text="time")],
        )

    def test_plural(self):
        self.assertEqual(
            runs("{Count:plural:time|times}", vars={"Count": 3}),
            [TextRun(text="times")],
        )

    def test_negative_one_is_singular(self):
        self.assertEqual(
            runs("{Count:plural:time|times}", vars={"Count": -1}),
            [TextRun(text="time")],
        )


# ---------------------------------------------------------------------------
# render_text_runs — suppressed placeholders
# ---------------------------------------------------------------------------


class TestRenderTextRunsSuppressed(unittest.TestCase):
    def test_in_combat_suppressed(self):
        self.assertEqual(runs("{InCombat}"), [])

    def test_energy_prefix_suppressed(self):
        self.assertEqual(runs("{energyPrefix}"), [])

    def test_single_star_icon(self):
        self.assertEqual(runs("{singleStarIcon}"), [TextRun(text="*")])


# ---------------------------------------------------------------------------
# render_text_runs — realistic combined markup
# ---------------------------------------------------------------------------


class TestRenderTextRunsCombined(unittest.TestCase):
    def test_ball_lightning_base(self):
        markup = "Deal {Damage} damage.\n[gold]Channel[/gold] 1 [gold]Lightning[/gold]."
        self.assertEqual(
            runs(markup, vars={"Damage": 7}),
            [
                TextRun(text="Deal "),
                TextRun(text="7", source_var="Damage"),
                TextRun(text=" damage.\n"),
                TextRun(text="Channel", style="gold"),
                TextRun(text=" 1 "),
                TextRun(text="Lightning", style="gold"),
                TextRun(text="."),
            ],
        )

    def test_relic_blue_var_gold_keyword(self):
        markup = "At the start of combat, gain [blue]{Block}[/blue] [gold]Block[/gold]."
        self.assertEqual(
            runs(markup, vars={"Block": 10}),
            [
                TextRun(text="At the start of combat, gain "),
                TextRun(text="10", source_var="Block", style="blue"),
                TextRun(text=" "),
                TextRun(text="Block", style="gold"),
                TextRun(text="."),
            ],
        )


# ---------------------------------------------------------------------------
# resolve_text
# ---------------------------------------------------------------------------


class TestResolveText(unittest.TestCase):
    def test_plain_and_runs(self):
        result = resolve_text("Deal {Damage} damage.", {"Damage": 7}, set(), upgraded=False)
        self.assertEqual(result.plain, "Deal 7 damage.")
        self.assertEqual(result.runs, [
            TextRun(text="Deal "),
            TextRun(text="7", source_var="Damage"),
            TextRun(text=" damage."),
        ])


# ---------------------------------------------------------------------------
# extract_numeric_symbols
# ---------------------------------------------------------------------------


class TestExtractNumericSymbols(unittest.TestCase):
    def test_const_int(self):
        self.assertEqual(extract_numeric_symbols("private const int _baseDamage = 5;"), {"_baseDamage": 5})

    def test_field_int(self):
        self.assertEqual(extract_numeric_symbols("private int _count = 3;"), {"_count": 3})

    def test_negative(self):
        self.assertEqual(extract_numeric_symbols("private const int _delta = -2;"), {"_delta": -2})


# ---------------------------------------------------------------------------
# extract_vars
# ---------------------------------------------------------------------------


class TestExtractVars(unittest.TestCase):
    def test_named_dynamic_var(self):
        self.assertEqual(extract_vars('new DynamicVar("PotionSlots", 4m)'), {"PotionSlots": 4})

    def test_power_var_generic(self):
        self.assertEqual(extract_vars("new PowerVar<ThornsPower>(3m)"), {"ThornsPower": 3})

    def test_typed_via_type_names(self):
        self.assertEqual(extract_vars("new BlockVar(10m, ValueProp.Unpowered)", {"BlockVar": "Block"}), {"Block": 10})

    def test_integer_no_m_suffix(self):
        self.assertEqual(extract_vars("new EnergyVar(1)", {"EnergyVar": "Energy"}), {"Energy": 1})

    def test_multiple_vars(self):
        content = "new PowerVar<StrengthPower>(1m),\nnew EnergyVar(1)"
        result = extract_vars(content, {"EnergyVar": "Energy"})
        self.assertEqual(result, {"StrengthPower": 1, "Energy": 1})

    def test_empty_content(self):
        self.assertEqual(extract_vars("public sealed class Foo : RelicModel {}"), {})


# ---------------------------------------------------------------------------
# extract_tips
# ---------------------------------------------------------------------------


class TestExtractTips(unittest.TestCase):
    def test_static(self):
        self.assertEqual(
            extract_tips("HoverTipFactory.Static(StaticHoverTip.Block)"),
            [HoverTip(kind="hover_tip_static", target="Block", source="HoverTipFactory.Static")],
        )

    def test_from_power(self):
        self.assertEqual(
            extract_tips("HoverTipFactory.FromPower<ThornsPower>()"),
            [HoverTip(kind="hover_tip_power", target="ThornsPower", source="HoverTipFactory.FromPower")],
        )

    def test_from_orb(self):
        self.assertEqual(
            extract_tips("HoverTipFactory.FromOrb<LightningOrb>()"),
            [HoverTip(kind="hover_tip_orb", target="LightningOrb", source="HoverTipFactory.FromOrb")],
        )

    def test_for_energy(self):
        self.assertEqual(
            extract_tips("HoverTipFactory.ForEnergy(this)"),
            [HoverTip(kind="hover_tip_energy", target="Energy", source="HoverTipFactory.ForEnergy")],
        )

    def test_deduplication(self):
        content = "HoverTipFactory.Static(StaticHoverTip.Block)\nHoverTipFactory.Static(StaticHoverTip.Block)"
        self.assertEqual(len(extract_tips(content)), 1)

    def test_none(self):
        self.assertEqual(extract_tips("public sealed class Foo {}"), [])


# ---------------------------------------------------------------------------
# to_jsonable
# ---------------------------------------------------------------------------


@dataclass
class _Inner:
    value: int
    label: str | None = None


@dataclass
class _Outer:
    name: str
    inner: _Inner
    items: list[str]
    empty: list[str]


class TestToJsonable(unittest.TestCase):
    def test_basic(self):
        obj = _Outer(name="test", inner=_Inner(value=42), items=["a"], empty=[])
        self.assertEqual(to_jsonable(obj), {"name": "test", "inner": {"value": 42}, "items": ["a"]})

    def test_none_fields_omitted(self):
        self.assertEqual(to_jsonable(_Inner(value=5, label=None)), {"value": 5})

    def test_list_of_dataclasses(self):
        self.assertEqual(to_jsonable([_Inner(value=1), _Inner(value=2)]), [{"value": 1}, {"value": 2}])

    def test_primitives_passthrough(self):
        self.assertEqual(to_jsonable(42), 42)
        self.assertEqual(to_jsonable("hello"), "hello")
        self.assertIs(to_jsonable(True), True)


if __name__ == "__main__":
    unittest.main()
