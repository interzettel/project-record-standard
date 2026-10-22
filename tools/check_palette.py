"""Checks the text colour roles used by the reference presentations."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def luminance(colour: str) -> float:
    """Returns relative luminance for an opaque six-digit sRGB colour."""
    values = [int(colour[i:i+2],16)/255 for i in [1,3,5]]
    linear = [v/12.92 if v<=0.04045 else ((v+0.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,[0.2126,0.7152,0.0722]))


def main() -> None:
    """Reports contrast ratios and fails a tested normal-text role below 4.5."""
    rows=[]
    for path in sorted((ROOT/'examples/themes').glob('*.json')):
        theme=json.loads(path.read_text())
        for mode in ['light','dark']:
            if mode not in theme:
                continue
            tokens=theme[mode]
            pairs=[('text','background'),('muted','background'),('muted','surface'),('accentText','accent')]
            pairs.append(('blocked' if 'blocked' in tokens else 'signalText','background'))
            if path.stem=='portfolio':
                pairs.append(('signalText','signal'))
            for foreground,background in pairs:
                a,b=sorted([luminance(tokens[foreground]),luminance(tokens[background])])
                ratio=(b+0.05)/(a+0.05)
                rows.append({'theme':path.stem,'mode':mode,'role':foreground+'/'+background,'ratio':round(ratio,2),'passed':ratio>=4.5})
    print(json.dumps({'tested':len(rows),'minimum':min(r['ratio'] for r in rows),'failures':[r for r in rows if not r['passed']]},indent=2))
    if any(not r['passed'] for r in rows):
        raise SystemExit(1)


if __name__=='__main__':
    main()
