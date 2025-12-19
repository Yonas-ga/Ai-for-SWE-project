class Colors:
    """
    A collection of 24-bit TrueColor ANSI escape sequences.
    """

    # --- Helper Method ---
    @staticmethod
    def _rgb(r: int, g: int, b: int) -> str:
        """Generates a 24-bit TrueColor ANSI foreground sequence."""
        return f"\033[38;2;{r};{g};{b}m"

    # --- Formatting & Reset ---
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    # --- Standard UI Colors (TrueColor) ---
    HEADER = _rgb.__func__(150, 100, 255)  # Light Purple/Lavender
    BLUE = _rgb.__func__(60, 140, 255)  # Soft Blue
    CYAN = _rgb.__func__(0, 210, 210)  # Teal/Cyan
    GREEN = _rgb.__func__(46, 204, 113)  # Emerald Green
    WARNING = _rgb.__func__(255, 215, 0)  # Gold/Yellow
    FAIL = _rgb.__func__(220, 50, 50)  # Error Red

    # 1=Highest, 8=Lowest priority
    # These are now accessible as Colors.CRITICAL, Colors.URGENT, etc.

    CRITICAL = _rgb.__func__(255, 0, 0)  # 1: Red
    HIGH = _rgb.__func__(255, 99, 0)  # 2: Orange-Red
    URGENT = _rgb.__func__(255, 165, 0)  # 3: Orange
    IMPORTANT = _rgb.__func__(255, 200, 0)  # 4: Yellow
    MODERATE = _rgb.__func__(64, 170, 255)  # 5: Cyan-ish
    LOWER = _rgb.__func__(30, 120, 255)  # 6: Blue
    MINOR = _rgb.__func__(50, 205, 50)  # 7: Light Green
    TRIVIAL = _rgb.__func__(0, 128, 0)  # 8: Green

    PRIORITY_COLORS = [
        CRITICAL,  # 1
        HIGH,  # 2
        URGENT,  # 3
        IMPORTANT,  # 4
        MODERATE,  # 5
        LOWER,  # 6
        MINOR,  # 7
        TRIVIAL  # 8
    ]

    @staticmethod
    def get_priority_color(priority: int) -> str:
        """Returns the TrueColor sequence for a given priority level (1-8)."""
        idx = max(1, min(priority, len(Colors.PRIORITY_COLORS))) - 1
        return Colors.PRIORITY_COLORS[idx]


if __name__ == "__main__":
    print(f"{Colors.HEADER}--- Example Tasks ---{Colors.ENDC}")
    print(f"{Colors.CRITICAL}Priority 1: System Meltdown{Colors.ENDC}")
    print(f"{Colors.URGENT}Priority 3: Database Lag{Colors.ENDC}")
    print(f"{Colors.MODERATE}Priority 5: User Ticket{Colors.ENDC}")
    print(f"{Colors.TRIVIAL}Priority 8: Routine Cleanup{Colors.ENDC}")

    # Change p to check
    p = 8
    print(f"{Colors.get_priority_color(p)}Dynamic Priority {p} Message{Colors.ENDC}")