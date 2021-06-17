class MempoolTransaction():
    allParentTxns = set()
    def __init__(self, txid, fee, weight, parents):
        self.txid = txid
        self.fee = int(fee)
        self.weight = int(weight)
        self.count = 1
        self.parents = parents.split(";")
        for parent in self.parents:
            if(parent in MempoolTransaction.allParentTxns):
                continue
            else:
                MempoolTransaction.allParentTxns.add(parent)
        self.visited = False

    #Static method to check if a transaction is parent 
    @staticmethod
    def isParent(txn):
        if(txn.txid in MempoolTransaction.allParentTxns):
            return True
        return False

    # Method to cumulate transaction weight and fee with all it' parents.
    def cumulate(self,mempoolTxns):
        self.visited = True
        for parent in self.parents:
            if(parent):
                parentTxn = mempoolTxns[parent]
                if (parentTxn.visited):
                    continue
                else:
                    [previousWeight, previousFee, previousCount] = parentTxn.cumulate(mempoolTxns)
                    self.weight += previousWeight
                    self.fee += previousFee
                    self.count += previousCount
        return[self.weight,self.fee,self.count]

    #Given an Indenpendent transaction, this method will make sure all the parents are inserted to the blockIds, before the child.
    def traverseParents(self,mempoolTxns,blockIds):
        self.visited = True
        for parent in self.parents:
            if(parent):
                parentTxn = mempoolTxns[parent]
                if(not parentTxn.visited):
                    parentTxn.traverseParents(mempoolTxns,blockIds)
        blockIds.append(self.txid)


class Mempool():

    def __init__(self):
        self.mempoolTxns = {}
        self.independentTxns = []
        
    def parse_mempool_csv(self):
        with open('mempool.csv') as f:
            for line in f.readlines()[1:]:
                params = line.strip().split(',')
                self.mempoolTxns[params[0]] = MempoolTransaction(*params)
    
    # This method will create list of independentTxns by cumulating all its parent.
    # So the child will have weights and fees of all its parent transaction.
    def equivalentIndependentTxns(self):
        for txid in self.mempoolTxns:
            currentTxn = self.mempoolTxns[txid]
            # We will ignore the transactions if 
            # - it is already visited
            # - or it is a parent of another transaction, as in that case it will be covered when we will deal with it;s child.
            if (currentTxn.visited or MempoolTransaction.isParent(currentTxn)):
                continue
            else:
                currentTxn.cumulate(self.mempoolTxns)
                self.independentTxns.append(currentTxn)

    # This method will now select independent transaction according to weight
    def selectIndependtentTxns(self, independentTxns, blockWeight):
        currentWeight = 0
        currentFee = 0
        selectedIndependtentTxns = []
        for i in range(len(independentTxns)):
            if(currentWeight + independentTxns[i].weight <= 4000000):
                currentWeight += independentTxns[i].weight
                currentFee += independentTxns[i].fee
                selectedIndependtentTxns.append(independentTxns[i].txid)
        print("Block Weight: "+str(currentWeight))
        print("Block Fee: "+str(currentFee))
        return selectedIndependtentTxns

    def visitedReset(self):
        for txid in self.mempoolTxns:
            currentTxn = self.mempoolTxns[txid]
            currentTxn.visited = False

    #Topologicl Sort for Independent transaction a sorted order
    def traverseDependencies(self,selectedIndependtentTxns):
        self.visitedReset()
        blockIds = []
        for txid in selectedIndependtentTxns:
            currentTxn = self.mempoolTxns[txid]
            if (currentTxn.visited):
                continue
            else:
                currentTxn.traverseParents(self.mempoolTxns, blockIds)
        return blockIds


    # Method to create block
    def createBlock(self, blockWeight=4000000):
        #Cumulate all the transaction
        self.equivalentIndependentTxns()
        #Sort by ratio between total fee and total weight for each block
        self.independentTxns.sort(key = lambda x: x.fee/x.weight,reverse = True)
        #Select best independent transaction according to constraint
        selectedIndependtentTxns = self.selectIndependtentTxns(self.independentTxns, blockWeight)
        #Method to get all the selected transaction included in the right order
        blockIds = self.traverseDependencies(selectedIndependtentTxns)
        #Writing to block.txt
        with open('block.txt', 'w') as f:
            for txid in blockIds:
                f.write("%s\n" % txid)
        
    
    #Check for valid block
    def checkValid(self,block):
        order = set()
        for txid in block:
            if(txid in order):
                print("Copy Of txid")
                print(txid)
            else:
                order.add(txid)
                for parent in self.mempoolTxns[txid].parents:
                    if(parent not in order):
                        print("Invalid Block")
                        return False
        
        return True


if __name__ == "__main__":
    # Creating mempool object
    mempool = Mempool()
    # Parsing
    mempool.parse_mempool_csv()
    #Creating block given contrain, blockWeight=4000000
    mempool.createBlock()
