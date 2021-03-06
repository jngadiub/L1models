#matching from https://github.com/gk199/Validation/blob/HoE_RatesWork/bin/rates.cxx#L373-L431
#for testing: python convertToh5.py -i /eos/cms/store/cmst3/user/jngadiub/L1TNtuple2018/data/ZeroBias/L1TNtuple_ZeroBias_Run2018C_PromptReco_v1/200803_121259/0000/L1Ntuple_72.root -o test.h5 --last 10 -v

import ROOT as rt
import numpy as np
import h5py
import sys, glob, os
import optparse
import math

def findMatching(offline_jet,event,verbose):

  minDR = 999999999.
  jMin = -99
  for j in range(event.nJets):
      myL1Jet = rt.TLorentzVector()
      # massless???
      myL1Jet.SetPtEtaPhiM(event.jetEt[j], event.jetEta[j], event.jetPhi[j], 0.)
      myDR = myL1Jet.DeltaR(offline_jet)
      if verbose: print("    - L1 jet",j,"pt",event.jetEt[j],"eta",event.jetEta[j],"phi",event.jetPhi[j],"dr_reco_l1",myDR)
      if myDR<minDR:
  	  minDR = myDR
  	  jMin = j
	  
  return jMin,minDR	  
		    
def Merge(inDir,outFileName,h5type):

    if os.path.isfile(outFileName):
     print "File",outFileName,"already exists... removing it!"
     os.system('rm '+outFileName)
     
    eventArray = np.array([])
    eventNames = ["event", "nPV", "isoMu", "nRecoJets","nL1Jets"]
    if h5type == 0:
     recoJetArray = np.array([])
     recoJetNames = ["pT", "eta", "phi", "isLeadingJet"]
    l1JetArray = np.array([])
    l1JetNames = ["pT", "eta", "phi", "Had", "Em", "HoE", "iEt","PUEt","jetPUDonutEt0","jetPUDonutEt1","jetPUDonutEt2","jetPUDonutEt3", "RawEt", "SeedEt"]
    Etemu = np.array([])
    Hademu = np.array([])
    Ememu = np.array([])
    Etaemu = np.array([])
    Phiemu = np.array([])
    
    FIRST = True
    files = glob.glob(inDir+"/*h5")
    
    #the eventTree is not always the same - reset names
    h5File = h5py.File(files[0],'r')
    eventNames = h5File['eventNames'][()]
    print(eventNames)
    h5File.close()
    
    for i,fileInName in enumerate(files):
    
        if i%10 == 0: print("File",i,"/",len(files))
		
        f = h5py.File(fileInName, "r")	
	   
        if FIRST:
         eventArray = np.array(f.get("eventInfo"))
         if h5type==0: recoJetArray = np.array(f.get("recoJet"))
         l1JetArray = np.array(f.get("l1Jet"))
	 if h5type!=2:
          Etemu = np.array(f.get("l1JetImage_Et"))
          Hademu = np.array(f.get("l1JetImage_Had")) 
          Ememu = np.array(f.get("l1JetImage_Em"))
          Etaemu = np.array(f.get("l1JetImage_Eta"))
          Phiemu = np.array(f.get("l1JetImage_Phi"))
         FIRST = False
        else: 	   
         eventArray = np.concatenate((eventArray, np.array(f.get("eventInfo"))), axis = 0)
         if h5type==0: recoJetArray = np.concatenate((recoJetArray, np.array(f.get("recoJet"))), axis = 0)
         l1JetArray = np.concatenate((l1JetArray, np.array(f.get("l1Jet"))), axis = 0)	 
	 if h5type!=2:
          Etemu = np.concatenate((Etemu, np.array(f.get("l1JetImage_Et"))), axis = 0)
          Hademu = np.concatenate((Hademu, np.array(f.get("l1JetImage_Had"))), axis=0)
          Ememu = np.concatenate((Ememu, np.array(f.get("l1JetImage_Em"))), axis=0)
          Etaemu = np.concatenate((Etaemu, np.array(f.get("l1JetImage_Eta"))), axis=0)
          Phiemu = np.concatenate((Phiemu, np.array(f.get("l1JetImage_Phi"))), axis=0)

    print("Final shapes:")
    if h5type==0: print("recoJet =",recoJetArray.shape)
    print("l1Jet =",l1JetArray.shape)
    if h5type!=2:
     print("l1JetImage_Et =",Etemu.shape)
     print("l1JetImage_Had =",Hademu.shape)
     print("l1JetImage_Em =",Ememu.shape)
     print("l1JetImage_Eta =",Etaemu.shape)
     print("l1JetImage_Phi =",Phiemu.shape)
    
    outFile = h5py.File(outFileName, "w")
    outFile.create_dataset('eventInfo', data=eventArray, compression='gzip')
    outFile.create_dataset('eventNames', data=eventNames, compression='gzip')
    if h5type==0:
     outFile.create_dataset('recoJet', data=recoJetArray, compression='gzip')
     outFile.create_dataset('recoJetNames', data=recoJetNames, compression='gzip')
    outFile.create_dataset('l1Jet', data=l1JetArray, compression='gzip')
    outFile.create_dataset('l1JetNames', data=l1JetNames, compression='gzip')
    if h5type!=2:
     outFile.create_dataset('l1JetImage_Et', data=Etemu, compression='gzip')
     outFile.create_dataset('l1JetImage_Had', data=Hademu, compression='gzip')
     outFile.create_dataset('l1JetImage_Em', data=Ememu, compression='gzip')
     outFile.create_dataset('l1JetImage_Eta', data=Etaemu, compression='gzip')
     outFile.create_dataset('l1JetImage_Phi', data=Phiemu, compression='gzip')
    outFile.close()
    		      
def Convert(options):


    # l1EventTree
    # l1CaloTowerTree
    # l1UpgradeTfMuonTree
    # l1UpgradeTree
    # l1uGTTree
    # l1HOTree
    # l1UpgradeTfMuonEmuTree
    # l1CaloTowerEmuTree
    # l1UpgradeEmuTree
    # l1uGTEmuTree
    # l1RecoTree
    # l1JetRecoTree
    # l1MetFilterRecoTree
    # l1ElectronRecoTree
    # l1TauRecoTree
    # l1MuonRecoTree
    # l1GeneratorTree

    eventArray = np.array([])
    eventNames = ["event", "nPV", "isoMu", "nRecoJets","nL1Jets","nMatchedJets"]
    recoJetArray = np.array([])
    recoJetNames = ["pT", "eta", "phi", "isLeadingJet"]
    l1JetArray = np.array([])
    l1JetNames = ["pT", "eta", "phi", "Had", "Em", "HoE", "iEt","PUEt","jetPUDonutEt0","jetPUDonutEt1","jetPUDonutEt2","jetPUDonutEt3", "RawEt", "SeedEt"]
    Etemu = np.array([])
    Hademu = np.array([])
    Ememu = np.array([])
    Etaemu = np.array([])
    Phiemu = np.array([])
    
    FIRST = True
    FIRSTEVT = True

    inFile = rt.TFile(options.infile, "r")
    l1EventTree = inFile.Get('l1EventTree/L1EventTree')
    l1Tree = inFile.Get("l1UpgradeEmuTree/L1UpgradeTree")  
    recoTree = inFile.Get("l1JetRecoTree/JetRecoTree")
    l1CaloTowers = inFile.Get("l1CaloTowerEmuTree/L1CaloTowerTree")
    muonTree = inFile.Get("l1MuonRecoTree/Muon2RecoTree")

    first_entry = 0
    last_entry = l1Tree.GetEntries()
    if options.first != 0: first_entry = options.first
    if options.last != -1: last_entry = options.last
    N_entries = last_entry-first_entry
    
    for e in range(first_entry,last_entry):
    
        if e%1000 == 0: print "Event",e,"/",N_entries

        #Check for at least one iso muon in the event.
        isoMu = False;
        muonTree.GetEntry(e)
        for m in range(muonTree.Muon.nMuons):
            if muonTree.Muon.hlt_isomu[m] == 1:
        	isoMu = True
        	break  
		
        l1EventTree.GetEntry(e)
	event_number = l1EventTree.Event.event
	npv = l1EventTree.Event.nPV_True
		
        recoTree.GetEntry(e)
        recoJet = recoTree.Jet
	
        l1Tree.GetEntry(e)
        evt = l1Tree.L1Upgrade

        isLeadingJet = True
	isLeadingJetTmp = True
        if options.verbose: print("***NEW EVENT:",event_number,"entry",e,"npv",npv,"isoMu",isoMu)
	
	nJets = 0
	if options.caloJets: nJets = recoJet.nCaloJets
	else: nJets = recoJet.nJets
	
	if options.verbose: print("Found",nJets,"reco jets")
	
	nMatchedJets = 0
        for i in range(nJets):

            myRecoJet = rt.TLorentzVector()
	    
	    if options.caloJets: myRecoJet.SetPtEtaPhiE(recoJet.caloEtCorr[i], recoJet.caloEta[i], recoJet.caloPhi[i], recoJet.caloE[i])
            else: myRecoJet.SetPtEtaPhiE(recoJet.etCorr[i], recoJet.eta[i], recoJet.phi[i], recoJet.e[i])
	    
	    if options.verbose: print(" * Reco jet",i,"pt",myRecoJet.Pt(),"eta",myRecoJet.Eta(),"phi",myRecoJet.Phi())
	    
            # look for the closest L1 jet	    
	    jMin,minDR = findMatching(myRecoJet,evt,options.verbose)
	    
            # quality cuts
            if minDR > 0.2: continue

	    if options.verbose: print("-----> FOUND MATCHING: reco jet",i,"L1 jet",jMin,"dR",minDR)
	    
	    nMatchedJets+=1
	    isLeadingJet=isLeadingJetTmp
	    isLeadingJetTmp=False

            closestsL1Jet = rt.TLorentzVector()
            # massless??? 
            closestsL1Jet.SetPtEtaPhiM(evt.jetEt[jMin], evt.jetEta[jMin], evt.jetPhi[jMin], 0.)
	    
            # seed Eta and Phi
            seedTowerIEta = evt.jetTowerIEta[jMin]
            seedTowerIPhi = evt.jetTowerIPhi[jMin]

            # retrieve its calotowers
            l1CaloTowers.GetEntry(e)
            l1Towemu = l1CaloTowers.L1CaloTower	                

            nTowemu = l1Towemu.nTower
            seedTowerHad = 0
            seedTowerEm = 0 
	    seedTower9x9Em = 0.
	    seedTower9x9Had = 0.
            
            my_Etemu  = np.zeros((1,9,9))
            my_Hademu = np.zeros((1,9,9))
            my_Ememu  = np.zeros((1,9,9))
            my_Etaemu = np.zeros((1,9,9))
            my_Phiemu = np.zeros((1,9,9))
            for towIt in range(nTowemu):
                towEtemu  = l1Towemu.iet[towIt]
                towHademu = l1Towemu.ihad[towIt]
                towEmemu  = l1Towemu.iem[towIt]
                towEtaemu = l1Towemu.ieta[towIt]
                towPhiemu = l1Towemu.iphi[towIt]
                
                for iSeedTowerIEta in range(-4,5):
                    for iSeedTowerIPhi in range(-4,5):
                        wrappedIPhi = seedTowerIPhi+iSeedTowerIPhi
                        if wrappedIPhi > 72: wrappedIPhi -= 72
                        if wrappedIPhi < 0: wrappedIPhi += 72
                        if towEtaemu == seedTowerIEta+iSeedTowerIEta and towPhiemu == wrappedIPhi:
                            my_Etemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4]  = towEtemu
                            my_Hademu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towHademu
                            my_Ememu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4]  = towEmemu
                            my_Etaemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towEtaemu
                            my_Phiemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towPhiemu
			    seedTower9x9Em += towEmemu;
			    seedTower9x9Had += towHademu;
 
	    HoE = 0.
	    if (seedTower9x9Had+seedTower9x9Em)!=0: HoE = seedTower9x9Had/(seedTower9x9Em+seedTower9x9Had)

            #my_event = np.array([event_number, npv, isoMu, nJets, evt.nJets, nMatchedJets])
	    #my_event = np.reshape(my_event, (1,my_event.shape[0]))
            my_recoJet = np.array([myRecoJet.Pt(), myRecoJet.Eta(), myRecoJet.Phi(), isLeadingJet])
            my_recoJet = np.reshape(my_recoJet, (1,my_recoJet.shape[0]))
            my_l1Jet = np.array([closestsL1Jet.Pt(), closestsL1Jet.Eta(), closestsL1Jet.Phi(), seedTower9x9Had, seedTower9x9Em, HoE, 
	                         evt.jetIEt[jMin], evt.jetPUEt[jMin], evt.jetPUDonutEt0[jMin], evt.jetPUDonutEt1[jMin], evt.jetPUDonutEt2[jMin], evt.jetPUDonutEt3[jMin],
				 evt.jetRawEt[jMin],evt.jetSeedEt[jMin]])
            my_l1Jet = np.reshape(my_l1Jet, (1,my_l1Jet.shape[0]))
            # ...

            # append info to arrays
            if FIRST:
	        #eventArray = my_event
                recoJetArray = my_recoJet
                l1JetArray = my_l1Jet
                Etemu = my_Etemu
                Hademu = my_Hademu
                Ememu = my_Ememu
                Etaemu = my_Etaemu
                Phiemu = my_Phiemu
                FIRST = False
            else:          
	        #eventArray = np.concatenate((eventArray, my_event), axis = 0)      
                recoJetArray = np.concatenate((recoJetArray, my_recoJet), axis = 0)
                l1JetArray = np.concatenate((l1JetArray, my_l1Jet), axis = 0)
                Etemu = np.concatenate((Etemu, my_Etemu), axis = 0)
                Hademu = np.concatenate((Hademu, my_Hademu), axis=0)
                Ememu = np.concatenate((Ememu, my_Ememu), axis=0)
                Etaemu = np.concatenate((Etaemu, my_Etaemu), axis=0)
                Phiemu = np.concatenate((Phiemu, my_Phiemu), axis=0)
		
        my_event = np.array([event_number, npv, isoMu, nJets, evt.nJets, nMatchedJets])
	my_event = np.reshape(my_event, (1,my_event.shape[0]))
	if FIRSTEVT: 
	 eventArray = my_event
	 FIRSTEVT = False
	else:
	 eventArray = np.concatenate((eventArray, my_event), axis = 0) 
	        
    outFile = h5py.File(options.outfile, "w")
    outFile.create_dataset('eventInfo', data=eventArray, compression='gzip')
    outFile.create_dataset('eventNames', data=eventNames, compression='gzip')
    outFile.create_dataset('recoJet', data=recoJetArray, compression='gzip')
    outFile.create_dataset('recoJetNames', data=recoJetNames, compression='gzip')
    outFile.create_dataset('l1Jet', data=l1JetArray, compression='gzip')
    outFile.create_dataset('l1JetNames', data=l1JetNames, compression='gzip')
    outFile.create_dataset('l1JetImage_Et', data=Etemu, compression='gzip')
    outFile.create_dataset('l1JetImage_Had', data=Hademu, compression='gzip')
    outFile.create_dataset('l1JetImage_Em', data=Ememu, compression='gzip')
    outFile.create_dataset('l1JetImage_Eta', data=Etaemu, compression='gzip')
    outFile.create_dataset('l1JetImage_Phi', data=Phiemu, compression='gzip')
    outFile.close()
    
def ConvertRates(options):

    eventArray = np.array([])
    eventNames = ["event", "nPV", "isoMu", "nRecoJets","nL1Jets"]
    l1JetArray = np.array([])
    l1JetNames = ["pT", "eta", "phi", "Had", "Em", "HoE", "iEt","PUEt","jetPUDonutEt0","jetPUDonutEt1","jetPUDonutEt2","jetPUDonutEt3", "RawEt", "SeedEt"]
    Etemu = np.array([])
    Hademu = np.array([])
    Ememu = np.array([])
    Etaemu = np.array([])
    Phiemu = np.array([])
        
    FIRST = True

    inFile = rt.TFile(options.infile, "r")
    l1EventTree = inFile.Get('l1EventTree/L1EventTree')
    l1Tree = inFile.Get("l1UpgradeEmuTree/L1UpgradeTree")  
    recoTree = inFile.Get("l1JetRecoTree/JetRecoTree")
    l1CaloTowers = inFile.Get("l1CaloTowerEmuTree/L1CaloTowerTree")
    muonTree = inFile.Get("l1MuonRecoTree/Muon2RecoTree")

    first_entry = 0
    last_entry = l1Tree.GetEntries()
    if options.first != 0: first_entry = options.first
    if options.last != -1: last_entry = options.last
    N_entries = last_entry-first_entry
    
    for e in range(first_entry,last_entry):
    
        if e%1000 == 0: print "Event",e,"/",N_entries

        #Check for at least one iso muon in the event.
        isoMu = False;
        muonTree.GetEntry(e)
        for m in range(muonTree.Muon.nMuons):
            if muonTree.Muon.hlt_isomu[m] == 1:
        	isoMu = True
        	break  
		
        l1EventTree.GetEntry(e)
	event_number = l1EventTree.Event.event
	npv = l1EventTree.Event.nPV_True
			
        l1Tree.GetEntry(e)
        evt = l1Tree.L1Upgrade

        if options.verbose: print("***NEW EVENT:",event_number,"entry",e,"npv",npv,"isoMu",isoMu)
	
	nJets = evt.nJets
	
	if options.verbose: print("Found",nJets,"L1 jets")
	
	if nJets == 0: continue
	i = 0 #take only leading L1 jet
		    
	if options.verbose: print("  * L1 jet",i,"pt",evt.jetEt[i],"eta",evt.jetEta[i],"phi",evt.jetPhi[i])	
	
        # seed Eta and Phi
        seedTowerIEta = evt.jetTowerIEta[i]
        seedTowerIPhi = evt.jetTowerIPhi[i]

        # retrieve its calotowers
        l1CaloTowers.GetEntry(e)
        l1Towemu = l1CaloTowers.L1CaloTower		    

        nTowemu = l1Towemu.nTower
        seedTowerHad = 0
        seedTowerEm = 0 
	seedTower9x9Em = 0.
	seedTower9x9Had = 0.
        
        my_Etemu  = np.zeros((1,9,9))
        my_Hademu = np.zeros((1,9,9))
        my_Ememu  = np.zeros((1,9,9))
        my_Etaemu = np.zeros((1,9,9))
        my_Phiemu = np.zeros((1,9,9))
        for towIt in range(nTowemu):
            towEtemu  = l1Towemu.iet[towIt]
            towHademu = l1Towemu.ihad[towIt]
            towEmemu  = l1Towemu.iem[towIt]
            towEtaemu = l1Towemu.ieta[towIt]
            towPhiemu = l1Towemu.iphi[towIt]
            
            for iSeedTowerIEta in range(-4,5):
        	for iSeedTowerIPhi in range(-4,5):
        	    wrappedIPhi = seedTowerIPhi+iSeedTowerIPhi
        	    if wrappedIPhi > 72: wrappedIPhi -= 72
        	    if wrappedIPhi < 0: wrappedIPhi += 72
        	    if towEtaemu == seedTowerIEta+iSeedTowerIEta and towPhiemu == wrappedIPhi:
        		my_Etemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4]  = towEtemu
        		my_Hademu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towHademu
        		my_Ememu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4]  = towEmemu
        		my_Etaemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towEtaemu
        		my_Phiemu[0, iSeedTowerIEta+4, iSeedTowerIPhi+4] = towPhiemu
	    		seedTower9x9Em += towEmemu;
	    		seedTower9x9Had += towHademu;
 
	HoE = 0.
	if (seedTower9x9Had+seedTower9x9Em)!=0: HoE = seedTower9x9Had/(seedTower9x9Em+seedTower9x9Had)

        my_event = np.array([event_number, npv, isoMu, nJets, evt.nJets])
	my_event = np.reshape(my_event, (1,my_event.shape[0]))
        my_l1Jet = np.array([evt.jetEt[i], evt.jetEta[i], evt.jetPhi[i], seedTower9x9Had, seedTower9x9Em, HoE, 
			     evt.jetIEt[i], evt.jetPUEt[i], evt.jetPUDonutEt0[i], evt.jetPUDonutEt1[i], evt.jetPUDonutEt2[i], evt.jetPUDonutEt3[i],
	    		     evt.jetRawEt[i],evt.jetSeedEt[i]])
        my_l1Jet = np.reshape(my_l1Jet, (1,my_l1Jet.shape[0]))
        # ...

        # append info to arrays
        if FIRST:
	    eventArray = my_event
            l1JetArray = my_l1Jet
            Etemu = my_Etemu
            Hademu = my_Hademu
            Ememu = my_Ememu
            Etaemu = my_Etaemu
            Phiemu = my_Phiemu
            FIRST = False
        else:	       
	    eventArray = np.concatenate((eventArray, my_event), axis = 0)      
            l1JetArray = np.concatenate((l1JetArray, my_l1Jet), axis = 0)
            Etemu = np.concatenate((Etemu, my_Etemu), axis = 0)
            Hademu = np.concatenate((Hademu, my_Hademu), axis=0)
            Ememu = np.concatenate((Ememu, my_Ememu), axis=0)
            Etaemu = np.concatenate((Etaemu, my_Etaemu), axis=0)
            Phiemu = np.concatenate((Phiemu, my_Phiemu), axis=0)
            
    outFile = h5py.File(options.outfile, "w")
    outFile.create_dataset('eventInfo', data=eventArray, compression='gzip')
    outFile.create_dataset('eventNames', data=eventNames, compression='gzip')
    outFile.create_dataset('l1Jet', data=l1JetArray, compression='gzip')
    outFile.create_dataset('l1JetNames', data=l1JetNames, compression='gzip')
    outFile.create_dataset('l1JetImage_Et', data=Etemu, compression='gzip')
    outFile.create_dataset('l1JetImage_Had', data=Hademu, compression='gzip')
    outFile.create_dataset('l1JetImage_Em', data=Ememu, compression='gzip')
    outFile.create_dataset('l1JetImage_Eta', data=Etaemu, compression='gzip')
    outFile.create_dataset('l1JetImage_Phi', data=Phiemu, compression='gzip')
    outFile.close()

def ConvertRatesHT(options):

    eventArray = np.array([])
    eventNames = ["event", "nPV", "isoMu", "nRecoJets","nL1Jets"]
    l1JetArray = np.array([])
    l1JetNames = ["pT", "eta", "phi", "Had", "Em", "HoE", "iEt","PUEt","jetPUDonutEt0","jetPUDonutEt1","jetPUDonutEt2","jetPUDonutEt3", "RawEt", "SeedEt"]
        
    FIRST = True

    inFile = rt.TFile(options.infile, "r")
    l1EventTree = inFile.Get('l1EventTree/L1EventTree')
    l1Tree = inFile.Get("l1UpgradeEmuTree/L1UpgradeTree")  
    recoTree = inFile.Get("l1JetRecoTree/JetRecoTree")
    l1CaloTowers = inFile.Get("l1CaloTowerEmuTree/L1CaloTowerTree")
    muonTree = inFile.Get("l1MuonRecoTree/Muon2RecoTree")

    first_entry = 0
    last_entry = l1Tree.GetEntries()
    if options.first != 0: first_entry = options.first
    if options.last != -1: last_entry = options.last
    N_entries = last_entry-first_entry
    
    for e in range(first_entry,last_entry):
    
        if e%1000 == 0: print "Event",e,"/",N_entries

        #Check for at least one iso muon in the event.
        isoMu = False;
        muonTree.GetEntry(e)
        for m in range(muonTree.Muon.nMuons):
            if muonTree.Muon.hlt_isomu[m] == 1:
        	isoMu = True
        	break  
		
        l1EventTree.GetEntry(e)
	event_number = l1EventTree.Event.event
	npv = l1EventTree.Event.nPV_True
			
        l1Tree.GetEntry(e)
        evt = l1Tree.L1Upgrade

        if options.verbose: print("***NEW EVENT:",event_number,"entry",e,"npv",npv,"isoMu",isoMu)
	
	nJets = evt.nJets
	
	if options.verbose: print("Found",nJets,"L1 jets")
			
	for i in range(nJets):
		    
		if options.verbose: print("  * L1 jet",i,"pt",evt.jetEt[i],"eta",evt.jetEta[i],"phi",evt.jetPhi[i])	
	
        	# seed Eta and Phi
        	seedTowerIEta = evt.jetTowerIEta[i]
        	seedTowerIPhi = evt.jetTowerIPhi[i]

        	# retrieve its calotowers
        	l1CaloTowers.GetEntry(e)
        	l1Towemu = l1CaloTowers.L1CaloTower		    

        	nTowemu = l1Towemu.nTower
        	seedTowerHad = 0
        	seedTowerEm = 0 
		seedTower9x9Em = 0.
		seedTower9x9Had = 0.
        
        	for towIt in range(nTowemu):
            		towEtemu  = l1Towemu.iet[towIt]
            		towHademu = l1Towemu.ihad[towIt]
            		towEmemu  = l1Towemu.iem[towIt]
            		towEtaemu = l1Towemu.ieta[towIt]
            		towPhiemu = l1Towemu.iphi[towIt]
            
            		for iSeedTowerIEta in range(-4,5):
        			for iSeedTowerIPhi in range(-4,5):
        	    			wrappedIPhi = seedTowerIPhi+iSeedTowerIPhi
        	    			if wrappedIPhi > 72: wrappedIPhi -= 72
        	    			if wrappedIPhi < 0: wrappedIPhi += 72
        	    			if towEtaemu == seedTowerIEta+iSeedTowerIEta and towPhiemu == wrappedIPhi:
	    					seedTower9x9Em += towEmemu;
	    					seedTower9x9Had += towHademu;
 
		HoE = 0.
		if (seedTower9x9Had+seedTower9x9Em)!=0: HoE = seedTower9x9Had/(seedTower9x9Em+seedTower9x9Had)

        	my_event = np.array([event_number, npv, isoMu, nJets, evt.nJets])
		my_event = np.reshape(my_event, (1,my_event.shape[0]))
        	my_l1Jet = np.array([evt.jetEt[i], evt.jetEta[i], evt.jetPhi[i], seedTower9x9Had, seedTower9x9Em, HoE, 
			     	     evt.jetIEt[i], evt.jetPUEt[i], evt.jetPUDonutEt0[i], evt.jetPUDonutEt1[i], evt.jetPUDonutEt2[i], evt.jetPUDonutEt3[i],
	    		     	     evt.jetRawEt[i],evt.jetSeedEt[i]])
        	my_l1Jet = np.reshape(my_l1Jet, (1,my_l1Jet.shape[0]))

        	# append info to arrays
        	if FIRST:
	    		eventArray = my_event
            		l1JetArray = my_l1Jet
            		FIRST = False
        	else:	       
	    		eventArray = np.concatenate((eventArray, my_event), axis = 0)      
            		l1JetArray = np.concatenate((l1JetArray, my_l1Jet), axis = 0)

            
    outFile = h5py.File(options.outfile, "w")
    outFile.create_dataset('eventInfo', data=eventArray, compression='gzip')
    outFile.create_dataset('eventNames', data=eventNames, compression='gzip')
    outFile.create_dataset('l1Jet', data=l1JetArray, compression='gzip')
    outFile.create_dataset('l1JetNames', data=l1JetNames, compression='gzip')
    outFile.close()
    
if __name__ == "__main__":

    parser = optparse.OptionParser()
    parser.add_option("--first","--first",dest="first",type=int,help="First entry",default=0)
    parser.add_option("--last","--last",dest="last",type=int,help="Last entry",default=-1)
    parser.add_option("-o","--outfile",dest="outfile",help="Output file name",default='L1Ntuple.h5')
    parser.add_option("-i","--infile" ,dest="infile" ,help="Input file name" ,default='L1Ntuple.root')
    parser.add_option("-d","--indir" ,dest="indir" ,help="Input dir with h5 files to be merged" ,default='./')
    parser.add_option("--merge","--merge",dest="merge", action="store_true", help="Merge h5 files",default=False)
    parser.add_option("--calo","--calo",dest="caloJets", action="store_true", help="Use calo jets",default=False)
    parser.add_option("-v","--verbose",dest="verbose", action="store_true", help="Verbosity",default=False)
    parser.add_option("--h5type","--h5type",dest="h5type",type=int,help="Which h5 type (efficiency/training versus rates)",default=0)    
    (options,args) = parser.parse_args()

    if options.merge:
    
     print "Output file:",options.outfile
     print "Input dir:",options.indir
     Merge(options.indir,options.outfile,options.h5type)
     sys.exit()
     
     
    print "Input file:",options.infile
    print "Output file:",options.outfile
    print "First entry:",options.first
    print "Last entry:",options.last
    print "Use calo jets:",options.caloJets

    if options.h5type == 0:
     print("********** Make h5 files for training or efficiency studies **********")
     Convert(options)
    elif options.h5type == 1:
     print("********** Make h5 files for SingleJet rates studies **********")
     ConvertRates(options)
    elif options.h5type == 2:
     print("********** Make h5 files for HT rates studies **********")
     ConvertRatesHT(options)
