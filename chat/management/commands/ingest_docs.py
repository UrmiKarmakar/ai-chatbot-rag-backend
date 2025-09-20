from django.core.management.base import BaseCommand
from documents.models import Document
from chat.ingestion import ingest_documents_bulk


class Command(BaseCommand):
    help = "Ingest all active documents from the database into the vector store."

    def handle(self, *args, **options):
        docs = Document.objects.filter(is_active=True).only(
            "id", "title", "content", "type", "category", "tags"
        )

        prepared = []
        for doc in docs:
            prepared.append({
                "content": doc.content,
                "metadata": {
                    "id": f"doc_{doc.id}",
                    "title": doc.title,
                    "type": getattr(doc, "type", None),
                    "category": getattr(doc, "category", None),
                    "tags": getattr(doc, "tags", []),
                    "source": "database",
                },
            })

        if not prepared:
            self.stdout.write(self.style.WARNING("No active documents found to ingest."))
            return

        success = ingest_documents_bulk(prepared)
        if success:
            self.stdout.write(self.style.SUCCESS(f"Ingested {len(prepared)} documents successfully."))
        else:
            self.stdout.write(self.style.ERROR("Failed to ingest documents."))
