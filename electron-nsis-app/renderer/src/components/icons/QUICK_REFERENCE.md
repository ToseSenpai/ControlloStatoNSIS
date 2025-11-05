# 🚀 Quick Reference - Sistema Icone

## Import Base

```tsx
import { Icons, IconSizes, IconColors } from '@icons';
```

## Utilizzo Rapido

```tsx
// Icona base
<Icons.File.Excel size={24} />

// Con colore
<Icons.Media.Start size={32} color="#22c55e" />

// Con dimensione standard
<Icons.Navigation.Home size={IconSizes.lg} />

// Con colore standard
<Icons.Status.Success
  size={IconSizes.xl}
  color={IconColors.success}
/>
```

## Categorie Icone

| Categoria | Esempio |
|-----------|---------|
| **File** | `Icons.File.Excel` |
| **Media** | `Icons.Media.Start` |
| **Window** | `Icons.Window.Close` |
| **Navigation** | `Icons.Navigation.Home` |
| **Status** | `Icons.Status.Success` |
| **Stats** | `Icons.Stats.BarChart` |
| **Control** | `Icons.Control.Settings` |
| **Utility** | `Icons.Utility.Trash` |
| **Browser** | `Icons.Browser.Chrome` |
| **Shipping** | `Icons.Shipping.Package` |

## Icone Animate

```tsx
import { LoadingIcon, LoveIcon } from '@icons/AnimatedIcons';

<LoadingIcon size={48} />
<LoveIcon size={48} />
<StatiIcon size={48} />
<StatisticsIcon size={48} />
```

## Dimensioni Standard

```tsx
IconSizes.xs   // 12px
IconSizes.sm   // 16px
IconSizes.md   // 20px (default)
IconSizes.lg   // 24px
IconSizes.xl   // 32px
IconSizes.xxl  // 48px
```

## Colori Standard

```tsx
IconColors.primary   // #2563eb (blu)
IconColors.success   // #22c55e (verde)
IconColors.warning   // #f59e0b (arancione)
IconColors.error     // #ef4444 (rosso)
IconColors.info      // #3b82f6 (blu chiaro)
IconColors.muted     // #94a3b8 (grigio)
```

## Animazioni CSS

```tsx
<Icon className="icon-pulse" />
<Icon className="icon-spin" />
<Icon className="icon-bounce" />
<Icon className="icon-hover-grow" />
```

## Wrapper Animazioni

```tsx
import { PulseIcon, SpinIcon } from '@icons/AnimatedIcons';

<PulseIcon icon={Heart} iconProps={{ size: 32 }} />
<SpinIcon icon={RefreshCw} iconProps={{ size: 24 }} />
```

## Esempi Completi

### Loading State
```tsx
{isLoading && (
  <LoadingIcon
    size={IconSizes.xl}
    color={IconColors.primary}
  />
)}
```

### Success/Error Feedback
```tsx
{status === 'success' && (
  <Icons.Status.Success
    size={IconSizes.lg}
    color={IconColors.success}
  />
)}

{status === 'error' && (
  <Icons.Status.Error
    size={IconSizes.lg}
    color={IconColors.error}
  />
)}
```

### Button con Icona
```tsx
<button>
  <Icons.Media.Start size={IconSizes.sm} />
  Avvia Processo
</button>
```

---

📚 **Documentazione completa:** `assets/ICONS_README.md`
🎨 **Demo interattiva:** `IconShowcase.tsx`
