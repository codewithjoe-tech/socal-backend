import opennsfw2 as n2




path = "media/user/posts/ai-training-naked-girl_BdhxOoP.jpg"

prob = n2.predict_image(path)

print(round(prob*10,2))