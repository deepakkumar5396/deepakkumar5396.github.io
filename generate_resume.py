from pathlib import Path


PAGE_WIDTH = 595.28
PAGE_HEIGHT = 841.89
MARGIN = 42
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)

TEXT = (0.17, 0.22, 0.28)
MUTED = (0.38, 0.44, 0.52)
ACCENT = (0.13, 0.49, 0.78)
ACCENT_DARK = (0.05, 0.12, 0.20)
ACCENT_SOFT = (0.91, 0.96, 1.0)
RULE = (0.78, 0.86, 0.94)
WHITE = (1.0, 1.0, 1.0)

OUTPUT_FILE = "Deepak_Kumar_Resume.pdf"


def escape_pdf(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def approximate_width(text: str, size: float) -> float:
    width = 0.0
    for char in text:
        if char == " ":
            width += 0.28
        elif char in ".,:;|!/":
            width += 0.24
        elif char in "-+":
            width += 0.30
        elif char in "()[]{}":
            width += 0.28
        elif char.isdigit():
            width += 0.56
        elif char in "iljtfr":
            width += 0.30
        elif char in "mwMW":
            width += 0.84
        elif char.isupper():
            width += 0.68
        else:
            width += 0.52
    return width * size


def wrap_text(text: str, width: float, size: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        trial = f"{current} {word}"
        if approximate_width(trial, size) <= width:
            current = trial
        else:
            lines.append(current)
            current = word

    lines.append(current)
    return lines


class PDFBuilder:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.commands: list[str] = []
        self.page_started = False
        self.y = 0.0
        self.start_page()
        self.draw_header()

    def start_page(self) -> None:
        if self.page_started:
            self.pages.append(self.commands)
        self.commands = []
        self.page_started = True
        self.y = PAGE_HEIGHT - MARGIN

    def finish(self) -> bytes:
        self.pages.append(self.commands)
        return self._render_pdf()

    def ensure_space(self, needed: float) -> None:
        if self.y - needed >= MARGIN:
            return

        self.start_page()
        self.write_page_heading()

    def write_page_heading(self) -> None:
        self.line(MARGIN, PAGE_HEIGHT - 32, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 32, RULE, 1)
        self.text(
            MARGIN,
            PAGE_HEIGHT - 22,
            "Deepak Kumar Resume",
            font="F2",
            size=10,
            color=MUTED
        )
        self.y = PAGE_HEIGHT - 48

    def draw_header(self) -> None:
        header_height = 108
        header_bottom = PAGE_HEIGHT - MARGIN - header_height
        self.rect(MARGIN, header_bottom, CONTENT_WIDTH, header_height, fill=ACCENT_DARK)
        self.rect(MARGIN, header_bottom, CONTENT_WIDTH, 6, fill=ACCENT)

        self.text(MARGIN + 18, PAGE_HEIGHT - 62, "DEEPAK KUMAR", font="F2", size=24, color=WHITE)
        self.text(
            MARGIN + 18,
            PAGE_HEIGHT - 82,
            "Software Developer | Backend Systems, AWS Infrastructure, and AI-Assisted Engineering",
            font="F1",
            size=11.5,
            color=ACCENT_SOFT
        )

        self.text(
            MARGIN + 18,
            PAGE_HEIGHT - 102,
            "Bangalore, India | Triveniganj, Supaul, Bihar 852139",
            font="F1",
            size=9.5,
            color=ACCENT_SOFT
        )
        self.text(
            MARGIN + 18,
            PAGE_HEIGHT - 118,
            "cusat.deepak12@gmail.com | +91 95346 11809",
            font="F1",
            size=9.5,
            color=ACCENT_SOFT
        )
        self.text(
            MARGIN + 18,
            PAGE_HEIGHT - 134,
            "linkedin.com/in/kumardeepakkg | github.com/deepakkumar5396",
            font="F1",
            size=9.5,
            color=ACCENT_SOFT
        )

        self.y = header_bottom - 26

    def section(self, title: str) -> None:
        self.ensure_space(32)
        self.text(MARGIN, self.y, title.upper(), font="F2", size=10, color=ACCENT)
        rule_start = MARGIN + min(approximate_width(title.upper(), 10) + 14, 160)
        self.line(rule_start, self.y - 3, PAGE_WIDTH - MARGIN, self.y - 3, RULE, 1)
        self.y -= 18

    def paragraph(self, text: str, size: float = 10.2, color: tuple[float, float, float] = TEXT) -> None:
        lines = wrap_text(text, CONTENT_WIDTH, size)
        needed = len(lines) * (size + 3.8) + 2
        self.ensure_space(needed)
        for line in lines:
            self.text(MARGIN, self.y, line, font="F1", size=size, color=color)
            self.y -= size + 3.8
        self.y -= 2

    def bullet_list(self, items: list[str], size: float = 9.8) -> None:
        for item in items:
            lines = wrap_text(item, CONTENT_WIDTH - 18, size)
            needed = len(lines) * (size + 3.2) + 2
            self.ensure_space(needed)
            self.circle(MARGIN + 3, self.y - 4, 1.7, ACCENT)
            first_x = MARGIN + 14
            self.text(first_x, self.y, lines[0], font="F1", size=size, color=TEXT)
            self.y -= size + 3.2
            for line in lines[1:]:
                self.text(first_x, self.y, line, font="F1", size=size, color=TEXT)
                self.y -= size + 3.2
            self.y -= 1

    def role(self, title: str, company: str, dates: str, location: str, stack: str, bullets: list[str]) -> None:
        meta_lines = wrap_text(f"{dates} | {location} | {stack}", CONTENT_WIDTH, 9.2)
        needed = 18 + len(meta_lines) * 12 + sum(len(wrap_text(b, CONTENT_WIDTH - 18, 9.8)) for b in bullets) * 13.2 + 16
        self.ensure_space(needed)

        self.text(MARGIN, self.y, f"{title} | {company}", font="F2", size=11.5, color=TEXT)
        self.y -= 13
        for line in meta_lines:
            self.text(MARGIN, self.y, line, font="F1", size=9.2, color=MUTED)
            self.y -= 11
        self.bullet_list(bullets, size=9.8)
        self.y -= 4

    def skill_group(self, label: str, value: str) -> None:
        text = f"{label}: {value}"
        lines = wrap_text(text, CONTENT_WIDTH, 9.8)
        needed = len(lines) * 13 + 2
        self.ensure_space(needed)
        for index, line in enumerate(lines):
            self.text(MARGIN, self.y, line, font="F1", size=9.8, color=TEXT)
            self.y -= 13
        self.y -= 1

    def text(self, x: float, y: float, text: str, font: str, size: float, color: tuple[float, float, float]) -> None:
        escaped = escape_pdf(text)
        r, g, b = color
        self.commands.append(
            f"BT /{font} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg 1 0 0 1 {x:.2f} {y:.2f} Tm ({escaped}) Tj ET"
        )

    def rect(self, x: float, y: float, width: float, height: float, fill: tuple[float, float, float]) -> None:
        r, g, b = fill
        self.commands.append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {width:.2f} {height:.2f} re f")

    def line(self, x1: float, y1: float, x2: float, y2: float, color: tuple[float, float, float], width: float) -> None:
        r, g, b = color
        self.commands.append(
            f"{width:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S"
        )

    def circle(self, x: float, y: float, radius: float, fill: tuple[float, float, float]) -> None:
        r, g, b = fill
        size = radius * 2
        self.commands.append(
            f"{r:.3f} {g:.3f} {b:.3f} rg {x - radius:.2f} {y - radius:.2f} {size:.2f} {size:.2f} re f"
        )

    def _render_pdf(self) -> bytes:
        objects: list[bytes] = []

        def add_object(data) -> int:
            payload = data.encode("latin-1") if isinstance(data, str) else data
            objects.append(payload)
            return len(objects)

        catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
        pages_id = add_object("<< /Type /Pages /Count 0 /Kids [] >>")
        font_regular_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_bold_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        info_id = add_object(
            "<< "
            f"/Title ({escape_pdf('Deepak Kumar Resume - Backend Developer - Node.js AWS Microservices')}) "
            f"/Author ({escape_pdf('Deepak Kumar')}) "
            f"/Subject ({escape_pdf('Backend Software Developer Resume')}) "
            f"/Keywords ({escape_pdf('Deepak Kumar, Backend Developer, Node.js, TypeScript, AWS, PostgreSQL, Neo4j, RabbitMQ, WebSockets, Microservices, Resume')}) "
            f"/Creator ({escape_pdf('generate_resume.py')}) "
            f"/Producer ({escape_pdf('Codex Resume Generator')}) "
            ">>"
        )

        page_ids: list[int] = []

        for commands in self.pages:
            content = "\n".join(commands) + "\n"
            content_bytes = content.encode("latin-1")
            content_id = add_object(
                b"<< /Length "
                + str(len(content_bytes)).encode("ascii")
                + b" >>\nstream\n"
                + content_bytes
                + b"endstream"
            )
            page_id = add_object(
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {PAGE_WIDTH:.2f} {PAGE_HEIGHT:.2f}] "
                f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            )
            page_ids.append(page_id)

        kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
        objects[pages_id - 1] = f"<< /Type /Pages /Count {len(page_ids)} /Kids [{kids}] >>".encode("latin-1")

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]

        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{index} 0 obj\n".encode("ascii"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_start = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        pdf.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

        pdf.extend(
            (
                f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R /Info {info_id} 0 R >>\n"
                f"startxref\n{xref_start}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(pdf)


def build_resume() -> bytes:
    pdf = PDFBuilder()

    pdf.section("Professional Summary")
    pdf.paragraph(
        "Backend-focused Software Developer with 4.5+ years of experience designing, building, and scaling "
        "production systems across eSports, FinTech, HealthTech, and Real Estate. Strong hands-on experience with "
        "Node.js, TypeScript, PostgreSQL, Neo4j, RabbitMQ, WebSockets, AWS infrastructure, payment gateway "
        "integrations, microservices, and AI-assisted engineering workflows. Proven ability to own backend "
        "architecture, cloud deployments, performance optimization, and end-to-end delivery for high-scale products."
    )

    pdf.section("Selected Impact")
    pdf.bullet_list(
        [
            "Currently leading the full eSports ecosystem and digital store for e& (Etisalat), supporting a 1.5M+ user base, 20K peak active gamers, and 99.9% uptime.",
            "Delivered real-time systems, reward-led commerce, and payment gateway integrations across PayPal, PayTabs, PhonePe, and Cashfree.",
            "Contributed to Rs. 4500+ crore revenue influence and reduced CRM operational costs by Rs. 10L per month through product digitization at Xanadu Reality.",
            "Enabled consultation recording and playback workflows for 6M+ users in the MFine mobile ecosystem."
        ],
        size=9.8
    )

    pdf.section("Core Competencies")
    pdf.skill_group("Backend Engineering", "Node.js, Express.js, NestJS, REST API Design, Microservices, WebSockets, Event-Driven Systems")
    pdf.skill_group("Programming Languages", "JavaScript, TypeScript, Python, C++, Core Java")
    pdf.skill_group("Databases and Search", "PostgreSQL, MySQL, MongoDB, Neo4j, Elasticsearch, PySpark")
    pdf.skill_group(
        "AWS and Infrastructure",
        "EC2, ECS, EKS, ECR, Lambda, EventBridge, S3, CloudFront, Route 53, VPC, IAM, ALB, API Gateway, Reverse Proxy"
    )
    pdf.skill_group("DevOps and Messaging", "RabbitMQ, Docker, Jenkins, CI/CD, Container Deployments, Release Workflows")
    pdf.skill_group("Security and Frontend", "JWT, OAuth 2.0, Keycloak, Cognito, React, Redux, Tailwind CSS")
    pdf.skill_group(
        "Payments, Compliance, and AI",
        "PayPal, PayTabs, PhonePe, Cashfree, AML, KYC, Digilocker, SurePass, Sandbox APIs, ChatGPT, Claude, Gemini, Codex, GitHub Copilot"
    )
    pdf.skill_group("Domains", "eSports, FinTech, HealthTech, Real Estate")

    pdf.section("Professional Experience")
    pdf.role(
        "Tech Lead",
        "Techno XO",
        "Mar 2025 - Present",
        "Bangalore, India",
        "Node.js, MongoDB, MySQL, AWS, WebSockets",
        [
            "Leading end-to-end delivery of the full eSports ecosystem and digital store for e& (Etisalat), supporting a 1.5M+ total user base and peak concurrency of 20K active gamers.",
            "Architected backend services for tournament hosting, real-time chat, top-ups, gift cards, and reward-led commerce using Node.js, WebSockets, MongoDB, MySQL, and AWS.",
            "Integrated PayPal, PayTabs, PhonePe, and Cashfree to strengthen multi-gateway payment reliability across player-facing transaction flows.",
            "Scaled cloud infrastructure and release workflows to sustain 99.9% uptime while mentoring a 5+ member engineering team."
        ]
    )
    pdf.role(
        "SDE - 1, Corporate Identity Platform and AML",
        "iBind Systems",
        "Mar 2024 - Jan 2025",
        "Bangalore, India",
        "Node.js, PostgreSQL, Neo4j, RabbitMQ, AWS",
        [
            "Designed backend services and microservices for AML, KYC, authentication, document verification, and admin-led compliance workflows.",
            "Modeled complex corporate ownership structures in Neo4j to support graph-based traversal, beneficial ownership analysis, and relationship-driven queries.",
            "Implemented RabbitMQ-powered background job pipelines and bulk processing flows for reliable asynchronous operations.",
            "Integrated Digilocker, SurePass, and Sandbox APIs and secured access flows with JWT, OAuth 2.0, and Keycloak."
        ]
    )
    pdf.role(
        "Software Developer",
        "Xanadu Reality",
        "Jun 2022 - Feb 2024",
        "Bangalore, India",
        "Node.js, React, PostgreSQL, MongoDB, PySpark",
        [
            "Built scalable product platforms that transformed offline real-estate operations and contributed to Rs. 4500+ crore FY revenue influence.",
            "Delivered high-availability portals for sales, presales, and channel partners, reducing CRM operational costs by Rs. 10L per month.",
            "Developed API-driven CRM extensions and real-time cloud telephony synchronization for business-critical workflows.",
            "Processed and standardized large-scale datasets using PySpark and Azure Blob Storage to improve analytics readiness and data quality."
        ]
    )
    pdf.role(
        "Associate Software Developer",
        "MFine",
        "Aug 2021 - May 2022",
        "Kochi, India",
        "Node.js, React Native, Twilio, AWS S3",
        [
            "Automated consultation recording workflows using Twilio Video Composition and AWS S3, enabling seamless playback for 6M+ mobile users.",
            "Improved large-dataset search and pagination performance through Elasticsearch-based query optimization.",
            "Built reusable React Native UI components and theming systems to improve consistency across the MFine mobile application."
        ]
    )

    pdf.section("Education")
    pdf.paragraph(
        "Master of Computer Application (MCA), Cochin University of Science and Technology | Jul 2018 - May 2021 | Kochi, India | CGPA: 7.2",
        size=9.8
    )

    pdf.section("Projects")
    pdf.bullet_list(
        [
            "eMazdoor Portal - Built a Django and React web application connecting migrant workers with job providers.",
            "Online Parking System - Developed a Django web application to discover and book parking slots online."
        ],
        size=9.8
    )

    pdf.section("Awards and Additional Information")
    pdf.bullet_list(
        [
            "Star Performer Award 2025 for exceptional performance and successful delivery of the e& eSports ecosystem.",
            "Solved 500+ data structures and algorithms problems.",
            "Languages: English and Hindi."
        ],
        size=9.8
    )

    return pdf.finish()


def main() -> None:
    output_path = Path(__file__).with_name(OUTPUT_FILE)
    output_path.write_bytes(build_resume())
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
