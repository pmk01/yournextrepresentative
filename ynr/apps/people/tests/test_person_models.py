from django_webtest import WebTest
from sorl.thumbnail import get_thumbnail

from candidates.tests.factories import faker_factory
from candidates.tests.uk_examples import UK2015ExamplesMixin
from candidates.tests.helpers import TmpMediaRootMixin
from moderation_queue.tests.paths import EXAMPLE_IMAGE_FILENAME
from people.models import Person, PersonImage
from people.tests.factories import PersonFactory
from popolo.models import Membership


class TestPersonModels(UK2015ExamplesMixin, TmpMediaRootMixin, WebTest):
    def test_get_display_image_url(self):
        person = PersonFactory(name=faker_factory.name())

        self.assertEqual(
            person.get_display_image_url(),
            "/static/candidates/img/blank-person.png",
        )

        pi = PersonImage.objects.create_from_file(
            EXAMPLE_IMAGE_FILENAME,
            "images/jowell-pilot.jpg",
            defaults={
                "person": person,
                "is_primary": True,
                "source": "Taken from Wikipedia",
                "copyright": "example-license",
                "user_notes": "A photo of Tessa Jowell",
            },
        )

        url = get_thumbnail(pi.image, "x64").url

        self.assertEqual(person.get_display_image_url(), url)

    def test_get_alive_now(self):
        alive_person = PersonFactory(name=faker_factory.name())
        PersonFactory(name=faker_factory.name(), death_date="2016-01-01")
        qs = Person.objects.alive_now()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.get(), alive_person)

    def test_current_elections_standing_down(self):
        person = PersonFactory(name=faker_factory.name())
        self.assertEqual(person.current_elections_standing_down(), [])
        Membership.objects.create(
            ballot=self.dulwich_post_ballot_earlier,
            party=self.ld_party,
            person=person,
            elected=True,
        )

        person.not_standing.add(self.election)
        self.assertEqual(
            person.current_elections_standing_down(), [self.election]
        )
