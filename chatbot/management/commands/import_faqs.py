import csv

from django.core.management.base import BaseCommand, CommandError

from chatbot.models import FAQ


class Command(BaseCommand):
    """
    Bulk-load FAQ rows from a CSV file.

    Usage:
        python manage.py import_faqs data/faqs.csv

    Expected CSV columns (header row required):
        question, answer, keywords, category, is_active
    """

    help = "Import FAQ rows from a CSV file (question,answer,keywords,category,is_active)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to the CSV file to import")

    def handle(self, *args, **options):
        csv_path = options["csv_path"]

        try:
            file = open(csv_path, newline="", encoding="utf-8")
        except FileNotFoundError:
            raise CommandError(f"File not found: {csv_path}")

        created_count = 0
        updated_count = 0

        with file:
            reader = csv.DictReader(file)
            required_columns = {"question", "answer", "keywords", "category"}
            if not required_columns.issubset(set(reader.fieldnames or [])):
                raise CommandError(
                    f"CSV must have these columns: {', '.join(sorted(required_columns))}"
                )

            for row in reader:
                question = row["question"].strip()
                if not question:
                    continue  # skip blank rows

                is_active_value = row.get("is_active", "true").strip().lower()
                is_active = is_active_value in ("true", "1", "yes", "")

                obj, created = FAQ.objects.update_or_create(
                    question=question,
                    defaults={
                        "answer": row["answer"].strip(),
                        "keywords": row["keywords"].strip(),
                        "category": row["category"].strip(),
                        "is_active": is_active,
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} new FAQ(s), updated {updated_count} existing one(s)."
            )
        )
