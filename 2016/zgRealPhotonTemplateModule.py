import ROOT

from math import cos, sqrt

ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaR

from PhysicsTools.NanoAODTools.postprocessing.tools import deltaPhi

class exampleProducer(Module):
    def __init__(self):
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("photon_sieie",  "F");
        self.out.branch("photon_pt",  "F");
        self.out.branch("photon_eta",  "F");
        self.out.branch("gen_weight",  "F");
        self.out.branch("lepton_pdg_id",  "I");
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = Collection(event, "Electron")
        muons = Collection(event, "Muon")
        jets = Collection(event, "Jet")
        photons = Collection(event, "Photon")
        genparts = Collection(event, "GenPart")

        selected_gen_photons = []

        tight_muons = []

        loose_but_not_tight_muons = []
        
        tight_electrons = []

        loose_but_not_tight_electrons = []
        
        selected_photons = []

        tight_jets = []

        if event.MET_pt < 35:
            return False

        mask1 = (1 << 0) | (1 << 7) | (1 << 8) | (1 << 12) | (1 << 13)
        mask2 = (1 << 0) | (1 << 8) | (1 << 13)

        for i in range(0,len(genparts)):

            #if genparts[i].pdgId == 22:

                #print str(int(genparts[i].statusFlags & (1 << 0) == (1 << 0))) + " " + str(int(genparts[i].statusFlags & (1 << 1) == (1 << 1))) + " " + str(int(genparts[i].statusFlags & (1 << 2) == (1 << 2))) + " " + str(int(genparts[i].statusFlags & (1 << 3) == (1 << 3))) + " " + str(int(genparts[i].statusFlags & (1 << 4) == (1 << 4))) + " " + str(int(genparts[i].statusFlags & (1 << 5) == (1 << 5))) + " " + str(int(genparts[i].statusFlags & (1 << 6) == (1 << 6))) + " " + str(int(genparts[i].statusFlags & (1 << 7) == (1 << 7))) + " " + str(int(genparts[i].statusFlags & (1 << 8) == (1 << 8))) + " " + str(int(genparts[i].statusFlags & (1 << 9) == (1 << 9))) + " " + str(int(genparts[i].statusFlags & (1 << 10) == (1 << 10))) + " " + str(int(genparts[i].statusFlags & (1 << 11) == (1 << 11))) + " " + str(int(genparts[i].statusFlags & (1 << 12) == (1 << 12)))  + " " + str(int(genparts[i].statusFlags & (1 << 13) == (1 << 13))) + " " + str(int(genparts[i].statusFlags & (1 << 14) == (1 << 14)))

            if genparts[i].pdgId == 22:
                if genparts[i].pdgId == 22 and ((genparts[i].statusFlags & mask1 == mask1) or (genparts[i].statusFlags & mask2 == mask2)):
                    selected_gen_photons.append(i)

        assert( len(selected_gen_photons) == 1)

        for i in range(0,len(muons)):

            if muons[i].pt < 20:
                continue

            if abs(muons[i].eta) > 2.4:
                continue

            if muons[i].tightId and muons[i].pfRelIso04_all < 0.15:
                tight_muons.append(i)
#            elif muons[i].pfRelIso04_all < 0.4:
            elif muons[i].pfRelIso04_all < 0.25:
                loose_but_not_tight_muons.append(i)

        for i in range (0,len(electrons)):

            if electrons[i].pt/electrons[i].eCorr < 20:
                continue
            
            if abs(electrons[i].eta+electrons[i].deltaEtaSC) > 2.5:
                continue

            if (abs(electrons[i].eta + electrons[i].deltaEtaSC) < 1.479 and abs(electrons[i].dz) < 0.1 and abs(electrons[i].dxy) < 0.05) or (abs(electrons[i].eta + electrons[i].deltaEtaSC) > 1.479 and abs(electrons[i].dz) < 0.2 and abs(electrons[i].dxy) < 0.1):

                if electrons[i].cutBased >= 3:
                    tight_electrons.append(i)

                elif electrons[i].cutBased >= 1:
                    loose_but_not_tight_electrons.append(i)

        for i in range (0,len(photons)):

            if photons[i].pt/photons[i].eCorr < 20:
                continue

            if not ((abs(photons[i].eta) < 1.4442) or (1.566 < abs(photons[i].eta) and abs(photons[i].eta) < 2.5) ):
                continue

#            if photons[i].pixelSeed:
#                continue

            if not photons[i].electronVeto:
                continue

            pass_lepton_dr_cut = True

            for j in range(0,len(tight_muons)):
                if deltaR(muons[tight_muons[j]].eta,muons[tight_muons[j]].phi,photons[i].eta,photons[i].phi) < 0.5:
                    pass_lepton_dr_cut = False

            for j in range(0,len(tight_electrons)):
                if deltaR(electrons[tight_electrons[j]].eta,electrons[tight_electrons[j]].phi,photons[i].eta,photons[i].phi) < 0.5:
                    pass_lepton_dr_cut = False

            if not pass_lepton_dr_cut:
                continue

            if deltaR(genparts[selected_gen_photons[0]].eta,genparts[selected_gen_photons[0]].phi,photons[i].eta,photons[i].phi) > 0.1:
                continue

            selected_photons.append(i)
                
        if len(tight_muons)+ len(loose_but_not_tight_muons) + len(tight_electrons) + len(loose_but_not_tight_electrons)!= 2:
            return False

        #print len(selected_photons)

        if not len(selected_photons) == 1:
            return False

        if len(tight_muons) == 2:

            i1 = tight_muons[0]

            i2 = tight_muons[1]

            if not event.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ and not event.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ:
                return False

            if muons[i1].pt < 20:
                return False

            if muons[i2].pt < 20:
                return False

            if abs(muons[i1].eta) > 2.4:
                return False

            if abs(muons[i2].eta) > 2.4:
                return False

            if muons[i1].pfRelIso04_all > 0.15:
                return False

            if muons[i2].pfRelIso04_all > 0.15:
                return False

            if not muons[i1].tightId:
                return False

            if not muons[i2].tightId:
                return False

            if muons[i1].charge == muons[i2].charge:
                return False

            if ((muons[i1].p4() + muons[i2].p4()).M() > 110) or ((muons[i1].p4() + muons[i2].p4()).M() < 70) :
                return False

            self.out.fillBranch("lepton_pdg_id",13)

        elif len(tight_electrons) == 2:

            i1 = tight_electrons[0]

            i2 = tight_electrons[1]

            if not event.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ:
                return False

            if electrons[i1].cutBased < 3:
                return False

            if electrons[i2].cutBased < 3:
                return False

            if electrons[i1].pt/electrons[i1].eCorr < 25:
                return False

            if electrons[i2].pt/electrons[i2].eCorr < 25:
                return False

            if abs(electrons[i1].eta) > 2.5:
                return False

            if abs(electrons[i2].eta) > 2.5:
                return False

            if electrons[i1].charge == electrons[i2].charge:
                return False

            if ((electrons[i1].p4() + electrons[i2].p4()).M() > 110) or ((electrons[i1].p4() + electrons[i2].p4()).M() < 70) :
                return False

            self.out.fillBranch("lepton_pdg_id",11)

        else:
            return False

        self.out.fillBranch("photon_sieie",photons[selected_photons[0]].sieie)
        self.out.fillBranch("photon_pt",photons[selected_photons[0]].pt)
        self.out.fillBranch("photon_eta",photons[selected_photons[0]].eta)

        try:
            self.out.fillBranch("gen_weight",event.Generator_weight)
        except:
            pass

        return True

exampleModule = lambda : exampleProducer()
