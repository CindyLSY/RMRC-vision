import speech_recognition as sr

r = sr.Recognizer()
m = sr.Microphone()

all_processed_outputs = []


for i in range(2):

    try:
        print("A moment of silence, please...")
        with m as source: r.adjust_for_ambient_noise(source)
        print("Set minimum energy threshold to {}".format(r.energy_threshold))

        print("Record phrase ",i,": ");
        
        print("Say something!")
        with m as source: audio = r.listen(source)
        print("Got it! Now to recognize it...")

        with open("microphone-results.wav", "wb") as f:
                f.write(audio.get_wav_data())
        
        # recognize speech using Google Speech Recognition
        value = r.recognize_google(audio,show_all = True)

        all_processed_outputs.append(value['alternative'])

            

    except KeyboardInterrupt:
        print("Stopped recording phrase ",i)
        pass


print(all_processed_outputs)


'''
# we need some special handling here to correctly print unicode characters to standard output
            if str is bytes:  # this version of Python uses bytes for strings (Python 2)
                print(u"You said {}".format(value).encode("utf-8"))
            else:  # this version of Python uses unicode for strings (Python 3+)
                print("You said {}".format(value))
        except sr.UnknownValueError:
            print("Oops! Didn't catch that")
        except sr.RequestError as e:
            print("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))
'''
