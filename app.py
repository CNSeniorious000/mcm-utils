from functools import cached_property, cache
from flask import Flask, render_template


class Team:
    all_awards = [
        "Outstanding Winner",
        "Finalist",
        "Meritorious Winner",
        "Honorable Mention",
        "Successful Participant",
        "Unsuccessful Participant",
    ]

    @cache
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, number, year=2022):
        self.number = number
        self.year = year

    @cached_property
    def pdf(self):
        import requests
        return requests.get(f"https://www.comap-math.com/mcm/{self.year}Certs/{self.number}.pdf").content

    @cached_property
    def image(self):
        import cv2
        filename = f"cache/{self.number}.png"
        image = cv2.imread(filename)
        if image is not None:
            return image[300:-150]

        import fitz
        # noinspection PyUnresolvedReferences
        document = fitz.open(stream=self.pdf)
        document[0].get_pixmap().save(filename)
        return cv2.imread(filename)[200:-150]

    def show(self, image=None):
        from matplotlib.pyplot import imshow, show
        imshow(image if image is not None else self.image)
        show()

    @cached_property
    def reader(self):
        from easyocr import Reader
        return Reader(["en"])

    @cached_property
    def text(self):
        return self.reader.readtext(self.image)

    def show_bbox(self, color=(255, 0, 0)):
        import numpy as np
        from cv2 import line
        img: np.ndarray = self.image.copy()
        for points, string, degree in self.text:
            c = (*color, round(degree * 255))
            # noinspection PyPep8Naming
            A, B, C, D = [tuple(map(round, point)) for point in points]
            line(img, A, B, c)
            line(img, B, C, c)
            line(img, C, D, c)
            line(img, D, A, c)

        self.show(img)

    @cached_property
    def last_text(self):
        return self.text[-1][1]

    @cached_property
    def award(self):
        from rapidfuzz.process import extractOne as extract_one
        text = [string for _, string, _ in self.text]
        ans = sorted((extract_one(award, text)[1], award) for award in self.all_awards)[-1]
        # print(ans)
        return ans[1]


app = Flask("MCM utils")


@app.get("/")
def homepage():
    return render_template("home.html")


@app.get("/query/<int:number>")
def query(number):
    return render_template("query.html", number=number, award=Team(number).award)
