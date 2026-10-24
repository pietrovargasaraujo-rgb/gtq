"""Execute the emitted .cs bytes in a narrow test VM. This is NOT the GTA engine.
Covers logic, file recovery and operand encoding; cannot validate the game ABI,
CLEO loader, keyboard mapping, rendering, Windows permissions or mod conflicts.
"""
import sys,struct,unittest,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build import SCHEMA,create,assemble,V,L,encode_arg
CONFIG={'initial_money':150,'work_card_fee':10,'transaction_amount':100,'autosave_ms':30000}
class VM:
 def __init__(self,files=None,config=None):
  self.code,self.labels=assemble(create(config or CONFIG).code)
  self.files={} if files is None else files; self.handles={}; self.locals=[0]*34
  self.cash=350; self.keys=set(); self.messages=[]; self.cond=False; self.stack=[]; self.fail_write=False
 def decode(self,pos):
  start=pos; op=struct.unpack_from('<H',self.code,pos)[0]; pos+=2; args=[]
  arity=SCHEMA[op&0x7fff]
  while arity<0 or len(args)<arity:
   t=self.code[pos]; pos+=1
   if t==0 and arity<0: break
   if t==1: a=struct.unpack_from('<i',self.code,pos)[0];pos+=4
   elif t==3: a=V(struct.unpack_from('<H',self.code,pos)[0]);pos+=2
   elif t==14:
    n=self.code[pos];pos+=1;a=self.code[pos:pos+n].decode('ascii');pos+=n
   else: raise AssertionError((start,'unknown type',t))
   args.append(a)
  return op,args,pos
 def get(self,a): return self.locals[a[1]] if isinstance(a,tuple) else a
 def put(self,a,value):
  assert isinstance(a,tuple) and a[0]=='v'; self.locals[a[1]]=value
 def run(self,label,max_steps=20000,on_wait=None):
  pc=self.labels[label]; self.stack=[]; frame=0
  for _ in range(max_steps):
   op,args,nxt=self.decode(pc); base=op&0x7fff; val=list(map(self.get,args)); pc=nxt
   if base in [0x19,0x1d,0x39,0x3b,0x256,0xaab,0xab0,0xa9a]:
    if base in [0x19,0x1d]: result=val[0]>val[1]
    elif base in [0x39,0x3b]: result=val[0]==val[1]
    elif base==0x256: result=True
    elif base==0xaab: result=val[0] in self.files
    elif base==0xab0: result=val[0] in self.keys
    elif base==0xa9a:
     path,mode,_=val; result=not(mode=='wb' and self.fail_write) and (mode=='wb' or path in self.files)
     handle=0
     if result:
      handle=max(self.handles,default=0)+1;self.handles[handle]=[path,0]
      if mode=='wb':self.files[path]=bytearray()
     self.put(args[2],handle)
    self.cond=not result if op&0x8000 else result
   elif base==0: pass
   elif base==1:
    self.locals[32]+=1;self.locals[33]+=1;frame+=1
    if on_wait is not None:on_wait(self,frame)
   elif base in [6,0x85]: self.put(args[0],val[1])
   elif base in [0xa,0x5a]:self.put(args[0],val[0]+val[1])
   elif base in [0xe,0x62]:self.put(args[0],val[0]-val[1])
   elif base==2:pc=-val[0]
   elif base==0x4d:
    if not self.cond:pc=-val[0]
   elif base==0x50:self.stack.append(pc);pc=-val[0]
   elif base==0x51:
    if not self.stack:return
    pc=self.stack.pop()
   elif base==0xd6: assert val==[0]
   elif base==0x109:self.cash+=val[1]
   elif base==0x10b:self.put(args[1],self.cash)
   elif base==0xad1:self.messages.append(val[0])
   elif base==0xa9b:del self.handles[val[0]]
   elif base==0xa9c:self.put(args[1],len(self.files[self.handles[val[0]][0]]))
   elif base in [0xa9d,0xa9e]:
    handle,size,_=val;path,cursor=self.handles[handle];assert size==4
    if base==0xa9d:self.put(args[2],struct.unpack_from('<i',self.files[path],cursor)[0])
    else:self.files[path][cursor:cursor+4]=struct.pack('<i',val[2])
    self.handles[handle][1]+=4
   else:raise AssertionError(hex(base))
  raise AssertionError('instruction budget exceeded')
 def seed(self,cash=150,bank=0,identity=0,work=0,account=0):
  self.cash=cash
  for n,x in [(2,cash),(3,bank),(4,identity),(5,work),(6,account),(7,0),(8,1)]:self.locals[n]=x
class Tests(unittest.TestCase):
 def test_operand_encoding_known_vectors(self):
  self.assertEqual(encode_arg(V(3)),b'\x03\x03\x00')
  self.assertEqual(encode_arg(150),b'\x01\x96\x00\x00\x00')
  self.assertEqual(encode_arg('rb'),b'\x0e\x02rb')
  self.assertEqual(assemble([(0,),'loop',(1,0),(2,L('loop'))])[0],bytes.fromhex('000001000100000000020001feffffff'))
 def test_every_jump_targets_instruction(self):
  vm=VM();pc=0;boundaries=set();jumps=[]
  while pc<len(vm.code):
   boundaries.add(pc);op,args,pc=vm.decode(pc)
   if op in [2,0x4d,0x50]:self.assertLess(args[0],0);jumps.append(-args[0])
  self.assertEqual(pc,len(vm.code));self.assertTrue(set(jumps)<=boundaries)
 def test_new_profile_round_trip(self):
  vm=VM();vm.seed();vm.run('SAVE');self.assertEqual(vm.locals[26],1)
  self.assertEqual(vm.locals[7],1);self.assertEqual(len(vm.files),1)
  restored=VM(vm.files);restored.run('LOAD')
  self.assertEqual(restored.locals[23],1);self.assertEqual(restored.locals[2:7],[150,0,0,0,0])
  self.assertFalse(vm.handles);self.assertFalse(restored.handles)
 def test_documents_require_id_and_charge_once(self):
  vm=VM();vm.seed();vm.run('ISSUE_WORK');self.assertEqual(vm.cash,150);self.assertEqual(vm.locals[5],0)
  vm.run('ISSUE_ID');self.assertEqual(vm.locals[4],100001)
  vm.run('ISSUE_WORK');self.assertEqual(vm.cash,140);self.assertEqual(vm.locals[5],1)
  vm.run('ISSUE_WORK');self.assertEqual(vm.cash,140)
  vm.run('ISSUE_ID');self.assertEqual(vm.cash,140)
 def test_work_card_insufficient_cash(self):
  for cash in [0,1,9]:
   vm=VM();vm.seed(cash=cash,identity=100001);vm.run('ISSUE_WORK')
   self.assertEqual(vm.cash,cash);self.assertEqual(vm.locals[5],0);self.assertFalse(vm.files)
 def test_bank_requires_documents(self):
  vm=VM();vm.seed();vm.run('OPEN_ACCOUNT');self.assertEqual(vm.locals[6],0)
  vm.run('DEPOSIT');self.assertEqual(vm.cash,150)
  vm.run('ISSUE_ID');vm.run('OPEN_ACCOUNT');self.assertEqual(vm.locals[6],1)
  vm.run('OPEN_ACCOUNT');self.assertEqual(vm.cash,150)
 def test_deposit_and_withdraw_and_limits(self):
  vm=VM();vm.seed(identity=100001,account=1)
  vm.run('DEPOSIT');self.assertEqual((vm.cash,vm.locals[3]),(50,100))
  generation=vm.locals[7];vm.run('DEPOSIT');self.assertEqual((vm.cash,vm.locals[3]),(50,100));self.assertEqual(vm.locals[7],generation)
  vm.run('WITHDRAW');self.assertEqual((vm.cash,vm.locals[3]),(150,0))
  vm.run('WITHDRAW');self.assertEqual((vm.cash,vm.locals[3]),(150,0))
  vm.seed(cash=999999999,bank=100,identity=100001,account=1);vm.run('WITHDRAW');self.assertEqual(vm.cash,999999999)
  vm.seed(cash=100,bank=999999999,identity=100001,account=1);vm.run('DEPOSIT');self.assertEqual(vm.locals[3],999999999)
 def test_randomized_conservation_and_recovery(self):
  vm=VM();vm.seed(cash=10000,identity=100001,account=1);rng=random.Random(42)
  for i in range(600):
   vm.run(rng.choice(['DEPOSIT','WITHDRAW']))
   self.assertEqual(vm.cash+vm.locals[3],10000)
   self.assertGreaterEqual(vm.cash,0);self.assertGreaterEqual(vm.locals[3],0)
   if i%50==0:
    restored=VM(vm.files);restored.run('LOAD')
    self.assertEqual(restored.locals[2:7],vm.locals[2:7])
 def test_truncated_latest_uses_backup(self):
  vm=VM();vm.seed();vm.run('SAVE');vm.cash=120;vm.run('SAVE_CURRENT')
  latest='CLEO\\RP_Ultimate_'+('A' if vm.locals[8]==0 else 'B')+'.dat'
  vm.files[latest]=vm.files[latest][:17]
  restored=VM(vm.files);restored.run('LOAD');self.assertEqual(restored.locals[23],1);self.assertEqual(restored.locals[2],150)
 def test_checksum_and_invalid_schema_rejected(self):
  vm=VM();vm.seed();vm.run('SAVE');path=next(iter(vm.files));original=bytes(vm.files[path])
  for offset,value in [(0,0),(4,2),(12,-1),(16,100),(20,15),(24,2),(28,1),(32,0)]:
   data=bytearray(original);struct.pack_into('<i',data,offset,value)
   restored=VM({path:data});restored.run('LOAD')
   self.assertEqual(restored.locals[23],0,(offset,value));self.assertEqual(restored.locals[22],1)
 def test_write_failure_preserves_previous_slot(self):
  vm=VM();vm.seed();vm.run('SAVE');old={k:bytes(x) for k,x in vm.files.items()}
  vm.fail_write=True;vm.cash=110;vm.run('SAVE_CURRENT')
  self.assertEqual(vm.locals[26],0);self.assertEqual(vm.locals[7],1)
  self.assertEqual(old,{k:bytes(x) for k,x in vm.files.items()})
 def test_generation_limit(self):
  vm=VM();vm.seed();vm.locals[7]=1000000;vm.run('SAVE');self.assertEqual(vm.locals[26],0);self.assertFalse(vm.files)
 def test_config_changes_output_behavior(self):
  vm=VM(config={**CONFIG,'work_card_fee':25,'transaction_amount':10});vm.seed(identity=100001,account=1)
  vm.run('ISSUE_WORK');self.assertEqual(vm.cash,125)
  vm.run('DEPOSIT');self.assertEqual((vm.cash,vm.locals[3]),(115,10))
 def test_activation_creates_only_after_confirmation(self):
  vm=VM()
  def confirm(vm,frame):vm.keys={118} if frame==3 else set()
  vm.run('ACTIVATE',on_wait=confirm)
  self.assertEqual(vm.cash,150);self.assertEqual(vm.locals[0],1);self.assertEqual(vm.locals[26],1)
  self.assertEqual(len(vm.files),1)
  restored=VM(vm.files);restored.cash=888
  restored.run('ACTIVATE',on_wait=confirm)
  self.assertEqual(restored.cash,150);self.assertEqual(restored.locals[0],1);self.assertEqual(restored.locals[26],1)
 def test_activation_cancel_leaves_money_and_files_unchanged(self):
  vm=VM()
  def cancel(vm,frame):vm.keys={119} if frame==3 else set()
  vm.run('ACTIVATE',on_wait=cancel)
  self.assertEqual(vm.cash,350);self.assertEqual(vm.locals[0],0);self.assertFalse(vm.files)
 def test_activation_corrupt_profile_does_not_reset(self):
  files={'CLEO\\RP_Ultimate_A.dat':bytearray(b'invalid')}
  vm=VM(files);vm.run('ACTIVATE')
  self.assertEqual(vm.cash,350);self.assertEqual(vm.locals[0],0)
  self.assertEqual(bytes(next(iter(files.values()))),b'invalid')
 def test_activation_disk_error_leaves_cash_unchanged(self):
  vm=VM();vm.fail_write=True
  vm.run('ACTIVATE',on_wait=lambda vm,frame:setattr(vm,'keys',{118} if frame==3 else set()))
  self.assertEqual(vm.cash,350);self.assertEqual(vm.locals[0],0)
if __name__=='__main__':unittest.main(verbosity=2)
