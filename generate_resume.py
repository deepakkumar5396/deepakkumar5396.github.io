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
            "Tech Lead | Distributed Systems, AWS Infrastructure, Microservices, and Production Delivery",
            font="F1",
            size=11.5,
            color=ACCENT_SOFT
        )

        self.text(
            MARGIN + 18,
            PAGE_HEIGHT - 102,
            "Bangalore, India",
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
            f"/Title ({escape_pdf('Deepak Kumar Resume - Tech Lead - Distributed Systems AWS Microservices')}) "
            f"/Author ({escape_pdf('Deepak Kumar')}) "
            f"/Subject ({escape_pdf('Tech Lead and Backend Systems Engineer Resume')}) "
            f"/Keywords ({escape_pdf('Deepak Kumar, Tech Lead, Backend Systems Engineer, Distributed Systems, Node.js, TypeScript, AWS, PostgreSQL, Neo4j, RabbitMQ, WebSockets, Microservices, System Design, Resume')}) "
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

        pdf = bytearray(b"%PDF-1.4\n% Codex Resume PDF\n")
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
    pdf.bullet_list(
        [
            "Tech Lead with 4.5+ years designing, building, and operating distributed backend systems with strong ownership across architecture, delivery, reliability, and production support.",
            "Expertise in microservices architecture, system design, REST APIs, real-time WebSocket services, event-driven workflows, payment integrations, and cloud-native platforms.",
            "Proven scale includes platforms serving 1.5M+ users, 20K peak active gamers, 99.9% uptime, and multi-gateway payment flows with strong reliability expectations.",
            "Hands-on AWS infrastructure ownership across ECS, EKS, Lambda, EventBridge, EC2, S3, CloudFront, ALB, API Gateway, VPC, IAM, RDS, CI/CD, and deployment automation.",
            "Performance-focused engineer with wins including 70% Neo4j query improvement, 60% Elasticsearch latency reduction, 45% API latency reduction, and 60% faster deployment cycles.",
            "Strong foundation in design patterns, scalability, operational excellence, mentoring, code quality, and full software development lifecycle best practices."
        ],
        size=9.8
    )

    pdf.section("Professional Experience")
    pdf.role(
        "Tech Lead - Backend Systems",
        "Techno XO Private Limited",
        "Mar 2025 - Present",
        "Bangalore, India",
        "Node.js, MongoDB, MySQL, AWS ECS, Lambda, EventBridge, WebSockets, CI/CD",
        [
            "Architected an end-to-end distributed eSports platform and digital store for e& (Etisalat), serving 1.5M+ users with 99.9% uptime and high-concurrency state management.",
            "Led system design and deployment of mission-critical microservices on AWS for tournament management, real-time communication, reward systems, payment processing, and commerce flows.",
            "Designed scalable real-time architecture using WebSockets to support low-latency player experiences and peak activity of 20K active gamers.",
            "Integrated PayPal, PayTabs, PhonePe, and Cashfree payment gateways across top-up, gift-card, and reward-led commerce workflows.",
            "Optimized cloud infrastructure to support 3x traffic growth while reducing deployment cycles from 45 minutes to 18 minutes through CI/CD automation.",
            "Mentored 5+ engineers on system design, code quality, production readiness, and operational excellence; awarded Star Performer 2025 for technical execution and leadership."
        ]
    )
    pdf.role(
        "SDE-1, Compliance and Identity Platform",
        "iBind Systems",
        "Mar 2024 - Jan 2025",
        "Bangalore, India",
        "Node.js, PostgreSQL, Neo4j, RabbitMQ, AWS, OAuth 2.0, Keycloak, JWT",
        [
            "Designed backend microservices for AML/KYC compliance workflows handling corporate identity verification, document verification, and beneficial ownership analysis at enterprise scale.",
            "Architected Neo4j graph database models for complex organizational relationships and optimized query performance by 70% through traversal design and indexing improvements.",
            "Built robust asynchronous processing pipelines with RabbitMQ for high-volume document verification and guaranteed delivery semantics.",
            "Integrated Digilocker, SurePass, Sandbox, and compliance APIs while maintaining secure service boundaries and reliable failure handling.",
            "Implemented authentication and authorization with OAuth 2.0, Keycloak, and JWT across compliance and admin systems."
        ]
    )
    pdf.role(
        "Software Engineer",
        "Xanadu Reality",
        "Jun 2022 - Feb 2024",
        "Bangalore, India",
        "Node.js, React, PostgreSQL, MongoDB, PySpark, Azure Blob Storage",
        [
            "Developed scalable backend platforms for real-estate digitization, supporting business units connected to Rs. 4500+ crore FY revenue impact.",
            "Engineered high-availability portals for sales, presales, and channel partner operations, reducing CRM operational costs by Rs. 10L/month through API-driven automation.",
            "Built API-driven CRM extensions, real-time cloud telephony synchronization, and business-critical workflows for sales operations.",
            "Optimized database and API performance through indexing, caching, and query improvements, reducing latency by 45% and improving throughput.",
            "Processed and standardized 10GB+ datasets using PySpark and Azure Blob Storage, improving data quality, analytics readiness, and business intelligence workflows."
        ]
    )
    pdf.role(
        "Associate Software Developer",
        "MFine",
        "Aug 2021 - May 2022",
        "Kochi, India",
        "Node.js, React Native, Twilio, AWS S3",
        [
            "Automated consultation recording, processing, and playback workflows for 6M+ mobile users using Twilio Video Composition and AWS S3.",
            "Optimized search infrastructure using Elasticsearch, achieving 60% latency reduction and efficient pagination for large-scale datasets.",
            "Built reusable React Native UI components and theming systems to improve consistency across the MFine mobile application."
        ]
    )

    pdf.section("Technical Skills")
    pdf.skill_group("Languages and Frameworks", "Node.js, Express, NestJS, TypeScript, JavaScript, Python, Java")
    pdf.skill_group("Data and Databases", "PostgreSQL, MySQL, MongoDB, Neo4j, Elasticsearch, Redis, PySpark")
    pdf.skill_group(
        "AWS Services",
        "EC2, ECS, EKS, Lambda, S3, CloudFront, ALB, API Gateway, EventBridge, IAM, VPC, RDS"
    )
    pdf.skill_group(
        "Tools and Platforms",
        "Docker, Kubernetes, Jenkins, Git, Terraform, Twilio, RabbitMQ, WebSockets, OAuth 2.0, Keycloak"
    )
    pdf.skill_group(
        "AI and Developer Tools",
        "ChatGPT, Claude, Gemini, GitHub Copilot, Codex, prompt engineering, AI-assisted debugging, AI-assisted architecture"
    )
    pdf.skill_group(
        "Domain Expertise",
        "Real-time systems, payment processing, AML/KYC compliance, high-availability design, scalability, operational excellence, SDLC best practices"
    )

    pdf.section("Education")
    pdf.paragraph(
        "Master of Computer Application (MCA), Cochin University of Science and Technology | Jul 2018 - May 2021 | Kochi, India | CGPA: 7.2",
        size=9.8
    )

    pdf.section("Key Achievements")
    pdf.bullet_list(
        [
            "Architected and operated a distributed eSports platform supporting 1.5M+ users, 20K peak active gamers, and 99.9% uptime.",
            "Led technical architecture decisions for mission-critical systems handling high-volume transactions, real-time communication, and complex state management.",
            "Improved performance across multiple systems: Neo4j queries by 70%, Elasticsearch latency by 60%, and API latency by 45%.",
            "Reduced deployment cycle time by 60% through CI/CD automation and stronger cloud release workflows.",
            "Mentored engineers through code reviews, design discussions, production readiness practices, and system design knowledge sharing.",
            "Contributed to Rs. 4500+ crore revenue influence and Rs. 10L/month CRM cost reduction through real-estate platform digitization.",
            "Demonstrated strong problem-solving across payments, compliance, real-time systems, cloud infrastructure, and large-scale data processing."
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
