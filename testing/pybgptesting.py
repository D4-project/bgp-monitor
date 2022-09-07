import pybgpstream


if __name__ == "__main__":
    stream = pybgpstream.BGPStream(project="ris-live")

    for e in stream:
        print(e)
