About the debugger script:

The debugger script receives a collection of files in ancient Greek, the sentences of which have been mostly recovered or labeled as noisy (which have gaps). Whether they are recovered or noisy sentences, they include words/phrases sometimes marked up in double brackets. Here's an example:

⸤Κλ⸥υτοφόρμιγγες Δ[ιὸς ὑ-] ⸤ψιμέδοντος πα[ρθέ]νοι,⸥ [–⏑⏑ Πι]ερίδες [–] [–]ενυφαι[⏑⏑––] [–⏑⏑]ο?υς, ἵνα κ[––] [–⏑]γαίας Ἰσθμί[ας] [––⏑]ν, εὐβούλου ν?[⏑–] [–⏑ γαμ]βρὸν Νηρέ[ος] [⏑⏑–] νάσοιό τ' ἐϋ[⏑ ⏑ ]αν, ἔνθ?[–⏑–] –⏑⏑–⏑⏑–– –⏑⏑–⏑⏑–– ⸤ὦ Πέλοπος λιπαρᾶς νάσου θεόδματοι πύλαι⸥

The goal here is to process all the supplied files and produce four collections of new files; each one linked to different versions of each one of the original ones. The four collections produced by the script correspond to the following sets of sentences: clean, noisy, strange and curated. Each collection of files is stored in folders with the same name and they are accessible at: ./ancient_greek_test/.

Clean sentences: These set includes only clean sentences both without restoration and those that have been restored.

Noisy sentences: They are noisy sentences whose gaps have been identified and marked up with spetial characters like –⏑⏑. For programming purposes it has been assumed that the above standard markup option defines the correct way to identify noisy regions in a sentence.

Strange sentences: These sentences correspond to those ones in which a noisy region does not follow the standard way of representation.

Curated (restored) sentences: Only restored sentences, free of noisy fragments, are listed in these files.

Beside the above, the debugger script generates a couple of indicators, related to the noise level of the files in the supplied corpus. These indicators are:

Noise rate: This indicator describes the proportion of noisy sentences in a file with respect to the total of them. This indicator includes both noisy sentences that follow the standard and the noisy sentences that do not.

	Noise rate = (standard noisy sentences + non standard noisy sentences)/sentences

Noise index: An indicator to measure the noise considering the amount of standard noisy fragments in a file and the number of non standard noisy sentences it includes.

	Index of noise = (standard noisy fragments + non standard noisy sentences)/sentences

The indicators above allow the reporting of the corpus' files, ordered according to the degree of related noise. The reports can be accessed at ./ancient_greek_test/report.

Follow these steps to run the script: 

1. Clone the repo:
	
	$ git clone https://github.com/jose-lopez/sentence-debugger

2. Change directory:

	$ cd sentence-debugger

3. and run the script:

	$ python3.9 ./src/utilities/debugger.py
