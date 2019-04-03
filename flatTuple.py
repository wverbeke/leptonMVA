import numpy as np
from ROOT import TTree, TFile 
import time 
from array import array

def isMuon( event, index ):
    return ( event._lFlavor[index] == 1 )


def isElectron( event, index ):
    return ( event._lFlavor[index] == 0 )


def isTau( event, index ):
    return ( event._lFlavor[index] == 2 )


def isGoodLeptonBase( event, index ):
	if abs( event._dxy[index] ) >= 0.05:
		return False
	if abs( event._dz[index] ) >= 0.1:
		return False 
	if abs( event._3dIPSig[index] ) >= 8:
		return False
	if abs( event._miniIso[index] ) >= 0.4:
		return False 
	return True


def isGoodMuon( event, index ):
    if not isMuon( event, index ):
        return False
    if event._lPt[index] < 5:
        return False
    if abs( event._lEta[index] ) >= 2.4:
    	return False
    if not isGoodLeptonBase( event, index ):
    	return False
    if not event._lPOGMedium[index]:
        return False
    return True 


def isGoodElectron( event, index ):
    if not isElectron( event, index ):
        return False
    if event._lPt[index] < 10:
        return False
    if abs( event._lEta[index] ) >= 2.5:
    	return False
    if not isGoodLeptonBase( event, index ):
    	return False
    if not event._lElectronPassEmu[index]:
        return False
    return True


def isPrompt( event, index ):
    if not event._lIsPrompt[index]:
        return False
    if event._lMatchPdgId[index] == 22:
        return False
    return True


def isNonprompt( event, index ):
    if event._lIsPrompt[index]:
        return False
    return True 


if __name__ == '__main__' :
    
    begin_time = time.perf_counter()

    #read original tree 
    original_file = TFile( 'noskim.root' )
    original_tree = original_file.Get( 'blackJackAndHookers/blackJackAndHookersTree' )
    
    #new flat tree 
    flat_file = TFile( 'flatTuple.root', 'RECREATE' )
    flat_tree = TTree( 'muonTree', 'muonTree' )

    max_jet_size = 100

    nClosestJetConstituents = array( 'i', [0])
    closestJetConstituentPt = array( 'f', [0]*max_jet_size)
    closestJetConstituentEta = array( 'f', [0]*max_jet_size)
    closestJetConstituentPhi = array( 'f', [0]*max_jet_size)
    closestJetConstituentPdgId = array( 'i', [0]*max_jet_size)
    closestJetConstituentCharge = array( 'i', [0]*max_jet_size)
    closestJetConstituentdxySig = array( 'f', [0]*max_jet_size)
    closestJetConstituentdzSig = array( 'f', [0]*max_jet_size)
    closestJetConstituentsNumberOfHits = array( 'i', [0]*max_jet_size)
    closestJetConstituentsNumberOfPixelHits = array( 'i', [0]*max_jet_size)
    closestJetConstituentsHasTrack = array( 'i', [0]*max_jet_size)
    lepIsPrompt = array( 'i', [0] )
    

    flat_tree.Branch( 'nClosestJetConstituents', nClosestJetConstituents, 'nClosestJetConstituents/i' )
    flat_tree.Branch( 'closestJetConstituentPt', closestJetConstituentPt, 'closestJetConstituentPt[{}]/F'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentEta', closestJetConstituentEta, 'closestJetConstituentEta[{}]/F'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentPhi', closestJetConstituentPhi, 'closestJetConstituentPhi[{}]/F'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentPdgId', closestJetConstituentPdgId, 'closestJetConstituentPdgId[{}]/I'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentCharge', closestJetConstituentCharge, 'closestJetConstituentCharge[{}]/I'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentdxySig', closestJetConstituentdxySig, 'closestJetConstituentdxySig[{}]/F'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentdzSig', closestJetConstituentdzSig, 'closestJetConstituentdzSig[{}]/F'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentsNumberOfHits', closestJetConstituentsNumberOfHits, 'closestJetConstituentsNumberOfHits[{}]/I'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentsNumberOfPixelHits', closestJetConstituentsNumberOfPixelHits, 'closestJetConstituentsNumberOfPixelHits[{}]/I'.format( max_jet_size ) )
    flat_tree.Branch( 'closestJetConstituentsHasTrack', closestJetConstituentsHasTrack, 'closestJetConstituentsHasTrack[{}]/i'.format( max_jet_size ) )
    flat_tree.Branch( 'lepIsPrompt', lepIsPrompt, 'lepIsPrompt/O' )
    
    for e, event in enumerate( original_tree ):
        original_tree.GetEntry( e )

        for i in range(event._nMu):

            if isGoodMuon( event, i ) and ( isNonprompt( event, i ) or isPrompt( event, i ) ):
                nClosestJetConstituents[0] = event._nClosestJetConstituents[i]
                lepIsPrompt[0] = isPrompt( event, i )

                for j in range(max_jet_size):

                    #convert flattened arrays (pyroot sucks) into 2d arrays 
                    closestJetConstituentPt[j] = event._closestJetConstituentPt[i*max_jet_size + j]
                    closestJetConstituentEta[j] = event._closestJetConstituentEta[i*max_jet_size + j]
                    closestJetConstituentPhi[j] = event._closestJetConstituentPhi[i*max_jet_size + j]
                    closestJetConstituentPdgId[j] = event._closestJetConstituentPdgId[i*max_jet_size + j]
                    closestJetConstituentCharge[j] = event._closestJetConstituentCharge[i*max_jet_size + j]
                    closestJetConstituentdxySig[j] = event._closestJetConstituentdxySig[i*max_jet_size + j]
                    closestJetConstituentdzSig[j] = event._closestJetConstituentdzSig[i*max_jet_size + j]
                    closestJetConstituentsNumberOfHits[j] = event._closestJetConstituentsNumberOfHits[i*max_jet_size + j]
                    closestJetConstituentsNumberOfPixelHits[j] = event._closestJetConstituentsNumberOfPixelHits[i*max_jet_size + j]
                    closestJetConstituentsHasTrack = 1 if event._closestJetConstituentsHasTrack[i*max_jet_size + j] else 0

                flat_tree.Fill() 

    flat_file.Write()
    flat_file.Close()

    end_time = time.perf_counter()
    print('Elapsed time = {} s'.format( end_time - begin_time ) )
