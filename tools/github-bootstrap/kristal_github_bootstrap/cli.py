from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .core import GhClient, BootstrapError, load_config, plan_account, apply_account, apply_single_repo


def main(argv=None):
    p=argparse.ArgumentParser(prog='kristal-github',description='Declarative GitHub bootstrap/reconciliation for Kristal v10 hosted networks.')
    p.add_argument('--dry-run',action='store_true')
    sub=p.add_subparsers(dest='command',required=True)
    doctor=sub.add_parser('doctor'); doctor.add_argument('--config',type=Path)
    plan=sub.add_parser('plan'); plan.add_argument('config',type=Path); plan.add_argument('--out',type=Path)
    apply=sub.add_parser('apply'); apply.add_argument('config',type=Path); apply.add_argument('--plan',type=Path); apply.add_argument('--yes',action='store_true'); apply.add_argument('--adopt-managed',action='store_true')
    status=sub.add_parser('status'); status.add_argument('config',type=Path)
    reconcile=sub.add_parser('reconcile'); reconcile.add_argument('config',type=Path); reconcile.add_argument('--yes',action='store_true'); reconcile.add_argument('--adopt-managed',action='store_true')
    repo=sub.add_parser('repo'); repo.add_argument('config',type=Path); repo.add_argument('--name',required=True); repo.add_argument('--visibility',choices=['public','private','internal'],required=True); repo.add_argument('--role',choices=['collection','directory','gateway','publisher'],default='collection'); repo.add_argument('--collection'); repo.add_argument('--no-register',action='store_true'); repo.add_argument('--yes',action='store_true'); repo.add_argument('--adopt-managed',action='store_true')
    args=p.parse_args(argv); client=GhClient(dry_run=args.dry_run)
    try:
        if args.command=='doctor':
            out=client.doctor();
            if args.config: out['plan']=plan_account(client,load_config(args.config))
            print(json.dumps(out,indent=2)); return 0
        cfg=load_config(args.config)
        if args.command in {'plan','status'}:
            out=plan_account(client,cfg)
            if args.command=='plan' and args.out: args.out.write_text(json.dumps(out,indent=2)+'\n'); print(str(args.out))
            else: print(json.dumps(out,indent=2))
            return 0
        if not args.yes and not args.dry_run: raise BootstrapError('refusing GitHub mutations without --yes; run plan first')
        if args.command in {'apply','reconcile'}:
            expected=None
            if getattr(args,'plan',None): expected=json.loads(args.plan.read_text()).get('observed_fingerprint')
            print(json.dumps(apply_account(client,cfg,overwrite=args.adopt_managed,expected_observed_fingerprint=expected),indent=2)); return 0
        if args.command=='repo':
            print(json.dumps(apply_single_repo(client,cfg,args.name,args.visibility,args.role,args.collection,not args.no_register,args.adopt_managed),indent=2)); return 0
    except BootstrapError as e:
        print(f'ERROR: {e}',file=sys.stderr); return 2

if __name__=='__main__': raise SystemExit(main())
