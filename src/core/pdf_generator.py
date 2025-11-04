from fpdf import FPDF

from .constants import HEADER_SIZE, PHASE_HEADER_SIZE, TEXT_SIZE, PHASE_COLORS
from .ability_timings import get_abilities_grouped_w_o_any
from src.constants import FONT_PATH

from src.logging_config import get_logger_for_package

logger = get_logger_for_package(__package__.split('.')[-1])


class AbilityPDF(FPDF):
    """
    Class for a PDF containing abilities sorted by timing.
    """

    def __init__(self, list_name):
        """
        Create a new AbilityPDF object.
        :param list_name: The name of the list.
        """
        super().__init__(orientation="P", unit="mm", format="A4")
        self.list_name = list_name

        # Add Unicode support
        self.add_font("OpenSans", "", FONT_PATH / "OpenSans-Regular.ttf", uni=True)
        self.add_font("OpenSans", "B", FONT_PATH / "OpenSans-Bold.ttf", uni=True)
        self.add_font("OpenSans", "I", FONT_PATH / "OpenSans-Italic.ttf", uni=True)
        self.add_font("OpenSans", "BI", FONT_PATH / "OpenSans-BoldItalic.ttf", uni=True)

        self.set_auto_page_break(auto=True)
        self.add_page()
        self.set_font("OpenSans", size=TEXT_SIZE)

    def header(self):
        """
        Insert a header containing the list name.
        """
        self.set_font("OpenSans", "B", HEADER_SIZE)
        self.cell(0, 10, self.list_name, ln=True, align="C")

    def make_phase_header(self, phase_name):
        """
        Insert a header for a given phase, colored accordingly
        :param phase_name: The name of the phase.
        """
        self.ln(5)
        self.set_font("OpenSans", "B", PHASE_HEADER_SIZE)
        # Set text color to white
        self.set_text_color(255, 255, 255)
        # Get right color for phase
        phase = next((p for p in PHASE_COLORS if p in phase_name), "Default")
        self.set_fill_color(*PHASE_COLORS[phase])
        self.cell(0, 10, phase_name, ln=True, align="L", fill=True)

    def make_ability_card(self, name: str, source: str, timing: str, declare: str | None, effect: str,
                          keywords: str | None, cost: str | None):
        """
        Insert information about an ability formatted in a 'card'.
        :param name: Name of the ability.
        :param source: Source of the ability (Unit/Battle Traits/...).
        :param timing: Timing of the ability.
        :param declare: Declare step of the ability.
        :param effect: Effect of the ability.
        :param keywords: Keywords of the ability.
        :param cost: Cost of the ability (CP/Casting/Chanting).
        """
        declare_key = "Declare: "
        effect_key = "Effect: "
        keywords_key = "Keywords: "

        # Ensure black text
        self.set_text_color(0, 0, 0)

        # Draw title card of ability
        self.ln(3)
        self.set_font("OpenSans", "B", TEXT_SIZE)
        title_card_text = f"{name} ({source})"
        title_card_text += f" -- {timing}" if timing is not None else ""
        self.multi_cell(0, 5, title_card_text, align="C", border=1)

        # Extract appropriate cost name
        declare_text = declare
        if cost is not None:
            declare_text = f"({cost}) -- {declare}"

        # Draw declare step if present
        if declare_text is not None:
            self.draw_key_value(declare_key, declare_text)

        # Draw effect step
        self.draw_key_value(effect_key, effect)

        # Draw keywords if present
        if keywords is not None:
            self.draw_key_value(keywords_key, keywords, styles=("B", "I"))

    def draw_key_value(self, key: str, value: str, styles: tuple[str, str] = ("B", "")):
        """
        Helper for inserting key, value pairs.
        :param key: the key
        :param value: the value
        :param styles: a tuple containing style identifiers (Optional, defaults to ("B", "")
        """
        self.ln(2)
        self.set_font("OpenSans", styles[0], TEXT_SIZE)
        self.cell(self.get_string_width(key), 5, key, align="L")
        self.set_font("OpenSans", styles[1], TEXT_SIZE)
        self.multi_cell(0, 5, value, align="L")


def generate_abilities_pdf(list_obj, filepath):
    """
    Creates an AbilityPDF object based on a List object and writes it to filepath.
    :param list_obj: The List object from which to create the AbilityPDF
    :param filepath: The filepath at which to write the AbilityPDF
    """
    grouped_abilities = get_abilities_grouped_w_o_any(list_obj)
    pdf = AbilityPDF(list_obj.name)

    logger.debug("Generating Ability PDF for %s", list_obj.name)

    for timing, abilities in grouped_abilities.items():
        # Don't display phases in which we don't have abilities
        unique_abilities = abilities
        if not unique_abilities:
            continue

        # Ensure that the phase header is never the last thing on a page
        first_ability = unique_abilities[0]
        with pdf.unbreakable() as doc:
            doc.make_phase_header(timing)
            doc.make_ability_card(
                first_ability.name,
                first_ability.source,
                first_ability.timing,
                first_ability.declare,
                first_ability.effect,
                first_ability.keywords,
                first_ability.cost
            )

        for ability in unique_abilities[1:]:
            # Ensure page break if ability doesn't fit on the page
            with pdf.unbreakable() as doc:
                doc.make_ability_card(
                    ability.name,
                    ability.source,
                    ability.timing,
                    ability.declare,
                    ability.effect,
                    ability.keywords,
                    ability.cost
                )

    logger.debug("Finished building PDF for %s", list_obj.name)

    pdf.output(str(filepath))

    logger.debug("Stored PDF at %s", filepath)
